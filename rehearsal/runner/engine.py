"""Deterministic evaluation runner and baseline intent/slot matcher for Rehearsal."""

from __future__ import annotations

import json
import logging
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from rehearsal.client.connector import MCPClientConnector
from rehearsal.runner.models import (
    CaseEvaluationResult,
    DomainEvaluationResult,
    EvaluationCase,
    EvaluationReport,
    PredictionResult,
    SlotMetrics,
)

logger = logging.getLogger("rehearsal.runner")

FIXTURES_DIR = Path(__file__).parent / "fixtures"


# -----------------------------------------------------------------------------
# Fixture Loader
# -----------------------------------------------------------------------------

def load_fixtures(
    fixtures_dir: Optional[Path] = None,
    domain: Optional[str] = None,
) -> List[EvaluationCase]:
    """Load and validate evaluation fixtures from JSON files."""
    target_dir = fixtures_dir or FIXTURES_DIR
    if not target_dir.exists():
        return []

    cases: List[EvaluationCase] = []
    json_files = sorted(target_dir.glob("*.json"))

    for filepath in json_files:
        if domain and filepath.stem != domain and not filepath.name.startswith(domain):
            continue
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    cases.append(EvaluationCase.model_validate(item))
        except Exception as exc:
            logger.error("Failed to load fixture file %s: %s", filepath, exc)
            raise

    return cases


# -----------------------------------------------------------------------------
# Speech Duration Estimator
# -----------------------------------------------------------------------------

def estimate_speech_duration(text: str, words_per_minute: int = 150) -> float:
    """Estimate spoken audio duration in seconds based on typical TTS reading speed (150 WPM)."""
    if not text or not text.strip():
        return 0.0
    words = len(text.strip().split())
    words_per_second = max(1.0, words_per_minute / 60.0)
    return round(words / words_per_second, 2)


# -----------------------------------------------------------------------------
# Deterministic Baseline Matcher
# -----------------------------------------------------------------------------

def _has_token(keywords: Sequence[str], text: str) -> bool:
    """Check if any keyword occurs as a whole word or phrase in text."""
    for kw in keywords:
        if " " in kw:
            if kw in text.lower():
                return True
        else:
            if re.search(r"\b" + re.escape(kw) + r"\b", text, re.IGNORECASE):
                return True
    return False


class BaselineIntentMatcher:
    """Transparent, deterministic rule-based matcher for mapping voice utterances to tools and arguments.

    This baseline evaluator does not rely on external LLM APIs and produces
    predictions independently of ground-truth test case expectations.
    """

    KNOWN_CITIES = ["Seattle", "New York", "London", "Boston", "Chicago", "San Francisco"]

    def predict(self, utterance: str) -> PredictionResult:
        """Analyze an utterance and independently predict tool, arguments, and abstention."""
        u_clean = utterance.strip()
        u_lower = u_clean.lower()

        # ---------------------------------------------------------------------
        # 1. Weather Domain
        # ---------------------------------------------------------------------
        if _has_token(["weather", "forecast", "rain", "temperature", "cold outside", "telemetry"], u_clean):
            # Flawed technical variant
            if _has_token(["telemetry", "sensor array", "geodetic", "coordinates"], u_clean):
                lat_match = re.search(r"(\d+\.?\d*)\s*(?:latitude|lat)", u_lower)
                lon_match = re.search(r"(-?\d+\.?\d*)\s*(?:longitude|lon)", u_lower)
                if lat_match and lon_match:
                    lat = float(lat_match.group(1))
                    lon = float(lon_match.group(1))
                    return PredictionResult(
                        predicted_tool="fetch_meteorological_telemetry_v2",
                        predicted_arguments={"spec": {"coordinates": {"latitude": lat, "longitude": lon}}},
                        is_abstention=False,
                    )

            # Voice-optimized tool: get_weather_summary
            city = self._extract_city(u_clean)
            if not city:
                # Underspecified request -> Abstain / Request clarification
                return PredictionResult(
                    predicted_tool=None,
                    predicted_arguments={},
                    is_abstention=True,
                    clarification_prompt="Which city or location would you like to check the weather for?",
                )

            timeframe = "today"
            if "tomorrow" in u_lower:
                timeframe = "tomorrow"
            elif "this weekend" in u_lower:
                timeframe = "this weekend"

            return PredictionResult(
                predicted_tool="get_weather_summary",
                predicted_arguments={"location": city, "timeframe": timeframe},
                is_abstention=False,
            )

        # ---------------------------------------------------------------------
        # 2. Smart Home Domain
        # ---------------------------------------------------------------------
        if _has_token(["lights", "fan", "lamp", "thermostat", "turn on", "switch off", "turn off", "dim", "turn it on", "rpc actuator"], u_clean):
            # Flawed technical variant
            if _has_token(["rpc", "guid", "register mask", "0x"], u_clean):
                hex_match = re.search(r"\b(0x[0-9a-fA-F\-]+)\b", u_clean)
                mask_match = re.search(r"register mask\s*(\d+)", u_lower)
                if hex_match:
                    guid = hex_match.group(1)
                    mask = int(mask_match.group(1)) if mask_match else 1
                    return PredictionResult(
                        predicted_tool="execute_home_iot_command_rpc",
                        predicted_arguments={"device_guid_hex": guid, "register_state_mask": mask},
                        is_abstention=False,
                    )

            # Voice-optimized tool: control_home_device
            room = self._extract_room(u_lower)
            device = self._extract_device(u_lower)

            if not room or not device:
                # Ambiguous / Underspecified (e.g., "Turn it on")
                return PredictionResult(
                    predicted_tool=None,
                    predicted_arguments={},
                    is_abstention=True,
                    clarification_prompt="Which room and device would you like to control?",
                )

            action = "turn on"
            if "switch off" in u_lower or "turn off" in u_lower:
                action = "turn off"
            elif "dim" in u_lower:
                action = "dim"

            return PredictionResult(
                predicted_tool="control_home_device",
                predicted_arguments={"room": room, "device": device, "action": action},
                is_abstention=False,
            )

        # ---------------------------------------------------------------------
        # 3. Travel Domain
        # ---------------------------------------------------------------------
        if _has_token(["flight", "flights", "fly", "gds", "itinerary", "book me a flight"], u_clean):
            # Flawed technical variant
            if any(term in u_lower for term in ["gds", "relational itinerary", "matrix", "iata", "2026-"]):
                iata_match = re.search(r"from\s+([A-Z]{3})\s+to\s+([A-Z]{3})", u_clean)
                date_match = re.search(r"(\d{4}-\d{2}-\d{2})", u_clean)
                if iata_match and date_match:
                    return PredictionResult(
                        predicted_tool="query_itinerary_and_schedule_matrix",
                        predicted_arguments={
                            "spec": {
                                "origin_iata": iata_match.group(1),
                                "dest_iata": iata_match.group(2),
                                "dates": {"depart_iso": date_match.group(1)},
                            }
                        },
                        is_abstention=False,
                    )

            # Voice-optimized tool: find_flight_summary
            origin, dest = self._extract_route(u_clean)
            if not origin or not dest:
                # Ambiguous / Underspecified request
                return PredictionResult(
                    predicted_tool=None,
                    predicted_arguments={},
                    is_abstention=True,
                    clarification_prompt="Which departure and arrival cities would you like to fly between?",
                )

            date = "this Friday"
            if "next monday" in u_lower:
                date = "next Monday"
            elif "tomorrow" in u_lower:
                date = "tomorrow"

            return PredictionResult(
                predicted_tool="find_flight_summary",
                predicted_arguments={"origin": origin, "destination": dest, "date": date},
                is_abstention=False,
            )

        # Out-of-domain / Negative requests
        return PredictionResult(
            predicted_tool=None,
            predicted_arguments={},
            is_abstention=True,
            clarification_prompt="I could not match this request to any available capability.",
        )

    def _extract_city(self, text: str) -> Optional[str]:
        for city in self.KNOWN_CITIES:
            if city.lower() in text.lower():
                return city
        # Regex fallback: in <City>
        match = re.search(r"\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", text)
        if match:
            return match.group(1).strip()
        return None

    def _extract_room(self, text: str) -> Optional[str]:
        for room in ["living room", "kitchen", "bedroom", "office", "bathroom"]:
            if room in text:
                return room
        return None

    def _extract_device(self, text: str) -> Optional[str]:
        for dev in ["lights", "fan", "lamp", "thermostat", "switch"]:
            if dev in text:
                return dev
        return None

    def _extract_route(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        match = re.search(r"from\s+([A-Za-z\s]+?)\s+to\s+([A-Za-z\s]+?)(?:\s+(?:this|next|tomorrow|for)|[.?$])", text, re.IGNORECASE)
        if match:
            orig = match.group(1).strip().title()
            dest = match.group(2).strip().title()
            return orig, dest
        return None, None


# -----------------------------------------------------------------------------
# Comparison & Metric Calculation Helpers
# -----------------------------------------------------------------------------

def _flatten_keys_and_values(d: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    """Recursively flatten nested argument dictionaries for slot comparison."""
    items: Dict[str, Any] = {}
    for k, v in d.items():
        full_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            items.update(_flatten_keys_and_values(v, full_key))
        else:
            items[full_key] = v
    return items


def compare_arguments(
    expected: Dict[str, Any],
    predicted: Dict[str, Any],
) -> Tuple[bool, List[str], List[str], List[str]]:
    """Compare expected and predicted slot arguments.

    Returns:
        (exact_match, matched_slots, missing_slots, unexpected_slots)
    """
    flat_exp = _flatten_keys_and_values(expected)
    flat_pred = _flatten_keys_and_values(predicted)

    matched: List[str] = []
    missing: List[str] = []
    unexpected: List[str] = []

    for k, v in flat_exp.items():
        if k in flat_pred:
            # Case-insensitive string comparison if strings
            exp_val = str(v).lower() if isinstance(v, str) else v
            pred_val = str(flat_pred[k]).lower() if isinstance(flat_pred[k], str) else flat_pred[k]
            if exp_val == pred_val:
                matched.append(k)
            else:
                missing.append(k)
        else:
            missing.append(k)

    for k in flat_pred.keys():
        if k not in flat_exp:
            unexpected.append(k)

    exact_match = (len(missing) == 0 and len(unexpected) == 0 and len(matched) == len(flat_exp))
    return exact_match, matched, missing, unexpected


# -----------------------------------------------------------------------------
# Main Evaluation Runner
# -----------------------------------------------------------------------------

async def run_evaluation(
    cases: Optional[Sequence[EvaluationCase]] = None,
    connector: Optional[MCPClientConnector] = None,
    matcher: Optional[BaselineIntentMatcher] = None,
) -> EvaluationReport:
    """Execute evaluation cases, calculate metrics, and compile an EvaluationReport.

    Args:
        cases: Evaluation test cases. If None, loads all fixtures from disk.
        connector: Optional active MCPClientConnector to invoke predicted tools for real outputs.
        matcher: Optional custom intent matcher. Defaults to BaselineIntentMatcher.

    Returns:
        Structured EvaluationReport.
    """
    test_cases = list(cases) if cases is not None else load_fixtures()
    intent_matcher = matcher or BaselineIntentMatcher()

    if not test_cases:
        return EvaluationReport(
            total_cases=0,
            correct_tool_selections=0,
            tool_selection_accuracy=0.0,
            exact_argument_matches=0,
            exact_argument_match_rate=0.0,
            slot_metrics=SlotMetrics(),
            missing_argument_count=0,
            unexpected_argument_count=0,
            total_abstentions=0,
            correct_abstentions=0,
        )

    case_results: List[CaseEvaluationResult] = []
    domain_cases: Dict[str, List[CaseEvaluationResult]] = {}

    total_expected_slots = 0
    total_predicted_slots = 0
    total_true_positives = 0
    total_missing = 0
    total_unexpected = 0
    speech_durations: List[float] = []

    for case in test_cases:
        # 1. Independent prediction
        prediction = intent_matcher.predict(case.utterance)

        # 2. Tool match evaluation
        tool_match = (prediction.predicted_tool == case.expected_tool)

        # 3. Argument comparison
        exact_args, matched_slots, missing_slots, unexpected_slots = compare_arguments(
            case.expected_arguments,
            prediction.predicted_arguments,
        )

        flat_exp = _flatten_keys_and_values(case.expected_arguments)
        flat_pred = _flatten_keys_and_values(prediction.predicted_arguments)
        total_expected_slots += len(flat_exp)
        total_predicted_slots += len(flat_pred)
        total_true_positives += len(matched_slots)
        total_missing += len(missing_slots)
        total_unexpected += len(unexpected_slots)

        # 4. Abstention check
        is_abstention_correct = (prediction.is_abstention == case.should_abstain)

        # 5. Optional live tool execution via MCP client connector
        tool_output: Optional[str] = None
        duration_sec: Optional[float] = None

        if connector and connector.is_connected and prediction.predicted_tool:
            try:
                call_res = await connector.call_tool(
                    prediction.predicted_tool,
                    prediction.predicted_arguments,
                )
                tool_output = connector.extract_text(call_res)
                duration_sec = estimate_speech_duration(tool_output)
                speech_durations.append(duration_sec)
            except Exception as exc:
                logger.debug("Tool call '%s' during evaluation returned error: %s", prediction.predicted_tool, exc)

        status = "PASS" if (tool_match and exact_args and is_abstention_correct) else "FAIL"

        case_res = CaseEvaluationResult(
            case_id=case.id,
            domain=case.domain,
            utterance=case.utterance,
            expected_tool=case.expected_tool,
            predicted_tool=prediction.predicted_tool,
            tool_match=tool_match,
            expected_arguments=case.expected_arguments,
            predicted_arguments=prediction.predicted_arguments,
            exact_argument_match=exact_args,
            matched_slots=matched_slots,
            missing_slots=missing_slots,
            unexpected_slots=unexpected_slots,
            is_abstention_correct=is_abstention_correct,
            tool_output=tool_output,
            estimated_speech_duration_seconds=duration_sec,
            status=status,
        )
        case_results.append(case_res)
        domain_cases.setdefault(case.domain, []).append(case_res)

    total_count = len(case_results)
    correct_tools = sum(1 for c in case_results if c.tool_match)
    tool_accuracy = round(correct_tools / total_count, 4) if total_count > 0 else 0.0

    exact_matches = sum(1 for c in case_results if c.exact_argument_match)
    exact_match_rate = round(exact_matches / total_count, 4) if total_count > 0 else 0.0

    precision = round(total_true_positives / total_predicted_slots, 4) if total_predicted_slots > 0 else 1.0
    recall = round(total_true_positives / total_expected_slots, 4) if total_expected_slots > 0 else 1.0
    f1 = round(2 * (precision * recall) / (precision + recall), 4) if (precision + recall) > 0 else 1.0

    slot_metrics = SlotMetrics(
        total_expected_slots=total_expected_slots,
        total_predicted_slots=total_predicted_slots,
        true_positives=total_true_positives,
        precision=precision,
        recall=recall,
        f1_score=f1,
    )

    # Per-domain breakdown
    per_domain: Dict[str, DomainEvaluationResult] = {}
    for dom, d_cases in domain_cases.items():
        d_total = len(d_cases)
        d_corr = sum(1 for c in d_cases if c.tool_match)
        d_exact = sum(1 for c in d_cases if c.exact_argument_match)
        per_domain[dom] = DomainEvaluationResult(
            domain=dom,
            total_cases=d_total,
            correct_tool_selections=d_corr,
            tool_selection_accuracy=round(d_corr / d_total, 4) if d_total > 0 else 0.0,
            exact_argument_matches=d_exact,
            exact_argument_match_rate=round(d_exact / d_total, 4) if d_total > 0 else 0.0,
        )

    total_abstain = sum(1 for c in test_cases if c.should_abstain)
    correct_abstain = sum(1 for c in case_results if c.is_abstention_correct and (c.expected_tool is None))
    avg_duration = round(sum(speech_durations) / len(speech_durations), 2) if speech_durations else 0.0

    return EvaluationReport(
        total_cases=total_count,
        correct_tool_selections=correct_tools,
        tool_selection_accuracy=tool_accuracy,
        exact_argument_matches=exact_matches,
        exact_argument_match_rate=exact_match_rate,
        slot_metrics=slot_metrics,
        missing_argument_count=total_missing,
        unexpected_argument_count=total_unexpected,
        total_abstentions=total_abstain,
        correct_abstentions=correct_abstain,
        average_estimated_speech_duration_seconds=avg_duration,
        per_domain_results=per_domain,
        case_results=case_results,
    )
