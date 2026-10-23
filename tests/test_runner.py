"""Automated tests for Rehearsal Deterministic Evaluation Runner.

Verifies:
1. Loading and validation of fixture files across all domains (15+ total cases).
2. Slot argument comparison and diff identification (matched, missing, unexpected).
3. Baseline matcher accuracy on direct, paraphrased, flawed, and negative utterances.
4. Correct handling of ambiguous queries and abstention/clarification outcomes.
5. Evaluation metrics calculation (Tool accuracy, Arg match rate, Slot Precision/Recall/F1).
6. Deterministic stability across repeated runs.
7. Safe handling of empty case collections.
8. Speech duration estimation based on reading speed (WPM).
9. Live integration with MCPClientConnector for real tool output & duration capture.
10. Report serialization to JSON and terminal dashboard rendering.
"""

import json
import pytest
from rehearsal.client import MCPClientConnector
from rehearsal.runner import (
    BaselineIntentMatcher,
    EvaluationCase,
    compare_arguments,
    estimate_speech_duration,
    load_fixtures,
    run_evaluation,
)


def test_fixture_loading_and_schema_validation():
    """Verify that all domain fixtures load properly and contain at least 5 cases each."""
    weather_cases = load_fixtures(domain="weather")
    smart_home_cases = load_fixtures(domain="smart_home")
    travel_cases = load_fixtures(domain="travel")
    all_cases = load_fixtures()

    assert len(weather_cases) >= 5
    assert len(smart_home_cases) >= 5
    assert len(travel_cases) >= 5
    assert len(all_cases) >= 15

    for case in all_cases:
        assert case.id and len(case.id) > 0
        assert case.domain in ["weather", "smart_home", "travel"]
        assert case.utterance and len(case.utterance) > 5
        assert case.rationale and len(case.rationale) > 5


def test_compare_arguments_logic():
    """Verify exact match, missing slots, and unexpected slots comparison."""
    # 1. Exact match
    exp = {"location": "Seattle", "timeframe": "today"}
    pred = {"location": "seattle", "timeframe": "today"}  # case-insensitive check
    exact, matched, missing, unexpected = compare_arguments(exp, pred)
    assert exact
    assert len(missing) == 0
    assert len(unexpected) == 0
    assert "location" in matched and "timeframe" in matched

    # 2. Missing slot
    pred_missing = {"location": "Seattle"}
    exact, matched, missing, unexpected = compare_arguments(exp, pred_missing)
    assert not exact
    assert "timeframe" in missing
    assert len(unexpected) == 0

    # 3. Unexpected slot
    pred_extra = {"location": "Seattle", "timeframe": "today", "extra": "val"}
    exact, matched, missing, unexpected = compare_arguments(exp, pred_extra)
    assert not exact
    assert "extra" in unexpected

    # 4. Nested dictionary comparison
    nested_exp = {"spec": {"coordinates": {"latitude": 47.6, "longitude": -122.3}}}
    nested_pred = {"spec": {"coordinates": {"latitude": 47.6, "longitude": -122.3}}}
    exact, matched, missing, unexpected = compare_arguments(nested_exp, nested_pred)
    assert exact
    assert "spec.coordinates.latitude" in matched


def test_baseline_matcher_intent_and_slot_predictions():
    """Verify matcher generates correct predictions independently of expected answers."""
    matcher = BaselineIntentMatcher()

    # Weather direct
    res_wx = matcher.predict("What is the weather in Seattle today?")
    assert res_wx.predicted_tool == "get_weather_summary"
    assert res_wx.predicted_arguments == {"location": "Seattle", "timeframe": "today"}
    assert not res_wx.is_abstention

    # Smart Home direct
    res_iot = matcher.predict("Turn on the living room lights.")
    assert res_iot.predicted_tool == "control_home_device"
    assert res_iot.predicted_arguments == {"room": "living room", "device": "lights", "action": "turn on"}

    # Travel direct
    res_travel = matcher.predict("Find flights from New York to London this Friday.")
    assert res_travel.predicted_tool == "find_flight_summary"
    assert res_travel.predicted_arguments == {"origin": "New York", "destination": "London", "date": "this Friday"}


def test_baseline_matcher_ambiguity_and_abstention():
    """Verify underspecified queries trigger abstention with recovery clarification prompts."""
    matcher = BaselineIntentMatcher()

    # Ambiguous weather missing city
    ambig_wx = matcher.predict("Is it cold outside right now?")
    assert ambig_wx.predicted_tool is None
    assert ambig_wx.is_abstention
    assert ambig_wx.clarification_prompt is not None

    # Ambiguous smart home missing room and device
    ambig_iot = matcher.predict("Turn it on.")
    assert ambig_iot.predicted_tool is None
    assert ambig_iot.is_abstention

    # Ambiguous travel missing origin and destination
    ambig_travel = matcher.predict("Book me a flight tomorrow morning.")
    assert ambig_travel.predicted_tool is None
    assert ambig_travel.is_abstention

    # Negative / out-of-domain request
    neg = matcher.predict("Play the latest news podcast episode on Spotify.")
    assert neg.predicted_tool is None
    assert neg.is_abstention


def test_speech_duration_estimation():
    """Verify speech duration calculation based on word count."""
    # 25 words at 150 WPM (2.5 words/sec) = 10.0 seconds
    sample_text = " ".join(["word"] * 25)
    duration = estimate_speech_duration(sample_text, words_per_minute=150)
    assert duration == 10.0

    assert estimate_speech_duration("") == 0.0
    assert estimate_speech_duration("   ") == 0.0


@pytest.mark.asyncio
async def test_evaluation_runner_determinism():
    """Running evaluation runner repeatedly yields identical accuracy and slot metrics."""
    cases = load_fixtures()
    report1 = await run_evaluation(cases)
    report2 = await run_evaluation(cases)

    assert report1.total_cases == report2.total_cases
    assert report1.tool_selection_accuracy == report2.tool_selection_accuracy
    assert report1.exact_argument_match_rate == report2.exact_argument_match_rate
    assert report1.slot_metrics.f1_score == report2.slot_metrics.f1_score
    assert report1.correct_tool_selections == report2.correct_tool_selections


@pytest.mark.asyncio
async def test_evaluation_runner_empty_cases_handling():
    """Verify running on empty cases does not raise ZeroDivisionError and produces empty report."""
    empty_report = await run_evaluation([])
    assert empty_report.total_cases == 0
    assert empty_report.tool_selection_accuracy == 0.0
    assert empty_report.exact_argument_match_rate == 0.0
    assert empty_report.slot_metrics.f1_score == 0.0


@pytest.mark.asyncio
async def test_evaluation_runner_live_connector_integration():
    """Verify evaluation runner integrates with MCPClientConnector to fetch outputs and durations."""
    cases = load_fixtures(domain="weather")[:3]
    async with MCPClientConnector() as client:
        report = await run_evaluation(cases, connector=client)
        assert report.total_cases == 3
        # Check that tool output was captured
        executed_cases = [c for c in report.case_results if c.predicted_tool is not None]
        assert len(executed_cases) > 0
        for ec in executed_cases:
            assert ec.tool_output and len(ec.tool_output) > 0
            assert ec.estimated_speech_duration_seconds is not None
            assert ec.estimated_speech_duration_seconds > 0.0


def test_report_serialization_and_summary():
    """Verify EvaluationReport serializes to valid JSON and formats terminal summary."""
    cases = load_fixtures()[:3]
    import asyncio
    report = asyncio.run(run_evaluation(cases))

    # JSON serialization
    json_str = report.to_json()
    parsed = json.loads(json_str)
    assert parsed["total_cases"] == 3
    assert "tool_selection_accuracy" in parsed
    assert "slot_metrics" in parsed

    # Terminal summary formatting
    summary = report.to_terminal_summary()
    assert "REHEARSAL EVALUATION SUITE REPORT" in summary
    assert "Tool Selection Accuracy:" in summary
    assert "Exact Argument Match Rate:" in summary
