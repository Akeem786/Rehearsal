"""Flawed reference MCP tools demonstrating common voice anti-patterns.

These tools are intentionally flawed in voice usability:
- Ambiguous or technical names and descriptions (poor discovery/selection).
- Deeply nested schemas or unutterable parameter names (poor ergonomics).
- Verbose, raw JSON, markdown tables, and hyperlink outputs (TTS hostility).
All implementations are deterministic and execute locally without external dependencies.
"""

from __future__ import annotations

import json
from typing import List
from pydantic import BaseModel, Field
from mcp.server import MCPServer


# -----------------------------------------------------------------------------
# Pair A: Weather (Flawed)
# Anti-pattern: Jargon name, nested geodetic coordinates, raw JSON telemetry dump
# -----------------------------------------------------------------------------

class GeoCoordinates(BaseModel):
    """Geodetic spatial coordinates."""
    latitude: float = Field(..., description="WGS84 latitude coordinate")
    longitude: float = Field(..., description="WGS84 longitude coordinate")


class SensorConfig(BaseModel):
    """Atmospheric sensor configuration parameters."""
    barometric_units: str = Field(default="hPa", description="Units: hPa, torr, or inHg")
    include_raw_kelvin: bool = Field(default=True, description="Output raw thermodynamic temperature")
    spectral_band_count: int = Field(default=16, description="Channel count for satellite radiation radiometer")


class TelemetryRequestSpec(BaseModel):
    """Nested payload specification for meteorological telemetry."""
    coordinates: GeoCoordinates = Field(..., description="Target latitude and longitude coordinate pair")
    sensor_config: SensorConfig = Field(default_factory=SensorConfig, description="Sensor hardware filter options")


def fetch_meteorological_telemetry_v2(spec: TelemetryRequestSpec) -> str:
    """Interface to query multi-spectral atmospheric sensor array records by spatial geodetic bounding box, returning unparsed telemetry dictionaries for climatological processing."""
    # Deterministic telemetry fixture based on lat/lon
    lat = spec.coordinates.latitude
    lon = spec.coordinates.longitude
    kelvin_temp = 287.15 + (lat % 10.0) - (abs(lon) % 5.0)

    raw_telemetry = {
        "status_header": {
            "query_epoch_timestamp_ms": 1729580400000,
            "station_identifier_hash": f"WX-STN-{abs(int(lat * 100)) % 9999:04d}",
            "sensor_array_health_bitmask": "0x00000001",
            "calibration_cycle_id": "CAL-2026-Q4-88A",
        },
        "atmospheric_telemetry": {
            "geodetic_latitude_wgs84": lat,
            "geodetic_longitude_wgs84": lon,
            "thermodynamic_temp_kelvin": round(kelvin_temp, 2),
            "dew_point_temp_kelvin": round(kelvin_temp - 4.5, 2),
            "barometric_pressure_pascals": 101325 + int(lat * 10),
            "relative_humidity_fractional": 0.742,
            "anemometer_vector": {
                "horizontal_velocity_mps": 4.12,
                "cardinal_azimuth_degrees": 235.8,
                "peak_gust_velocity_mps": 7.45,
            },
            "radiometer_spectral_bands_watts_per_m2": [
                0.12, 0.45, 0.89, 1.23, 0.98, 0.65, 0.32, 0.11,
                0.05, 0.02, 0.01, 0.01, 0.00, 0.00, 0.00, 0.00
            ][:spec.sensor_config.spectral_band_count],
        },
        "raw_checksum_crc32": "0xB7A249F1",
    }
    return json.dumps(raw_telemetry, indent=2)


# -----------------------------------------------------------------------------
# Pair B: Smart Home (Flawed)
# Anti-pattern: Opaque RPC name, hexadecimal MAC/GUID parameter, markdown table output
# -----------------------------------------------------------------------------

def execute_home_iot_command_rpc(
    device_guid_hex: str,
    register_state_mask: int = 1,
    cluster_routing_depth: int = 3,
) -> str:
    """Low-level binary RPC actuator dispatcher for local Zigbee/Z-Wave peripheral nodes across configured network clusters."""
    if not device_guid_hex or len(device_guid_hex.strip()) < 4:
        return "ERROR 0x7E: Device GUID missing or malformed bit length."

    # Returns a TTS-hostile markdown table with raw register states and URLs
    table_response = (
        "### Zigbee Actuator Diagnostic Report\n\n"
        "| Node GUID | Cluster ID | Register Mask | Hop Depth | Status Code | Diagnostic Checksum |\n"
        "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
        f"| `{device_guid_hex}` | `0x0006_ONOFF` | `{register_state_mask:#06x}` | "
        f"`{cluster_routing_depth}` | `200_COMMAND_DISPATCHED` | `0xDEADBEEF42` |\n\n"
        "Raw payload dispatched across PAN coordinator. "
        "Review [Topology Map](http://192.168.1.1:8080/diagnostics/zdo/topology?cluster=6) for packet ack trace."
    )
    return table_response


# -----------------------------------------------------------------------------
# Pair C: Travel / Itinerary (Flawed)
# Anti-pattern: GDS matrix query, strict 3-letter IATA codes, wall of text with links
# -----------------------------------------------------------------------------

class DateRangeWindow(BaseModel):
    """Calendar search window."""
    depart_iso: str = Field(..., description="Departure date in YYYY-MM-DD format")
    return_iso: str = Field(default="", description="Return date in YYYY-MM-DD format")


class ItineraryQuerySpec(BaseModel):
    """Detailed multi-tenant itinerary query payload."""
    origin_iata: str = Field(..., description="Origin 3-letter IATA code, e.g., 'JFK'")
    dest_iata: str = Field(..., description="Destination 3-letter IATA code, e.g., 'LHR'")
    dates: DateRangeWindow = Field(..., description="Date range object")
    fare_class_tier_flags: List[str] = Field(
        default_factory=lambda: ["Y", "B", "M"],
        description="Aviation reservation booking designator codes"
    )


def query_itinerary_and_schedule_matrix(spec: ItineraryQuerySpec) -> str:
    """Multi-tenant GDS relational itinerary availability matrix engine for aviation and calendar ledger lookups."""
    origin = spec.origin_iata.upper()
    dest = spec.dest_iata.upper()

    response = (
        f"## GDS Matrix Availability Results: {origin} -> {dest}\n\n"
        f"Query timestamp: 2026-10-22T05:00:00Z | Search Window: {spec.dates.depart_iso}\n"
        f"Active fare class buckets: {', '.join(spec.fare_class_tier_flags)}\n\n"
        "| Flight # | Carrier | Equip | Dep (UTC) | Arr (UTC) | Stops | Avail Seats | Base Fare | Direct Booking URL |\n"
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
        f"| BA0178 | British Airways | 777-300ER | {spec.dates.depart_iso}T08:15:00Z | {spec.dates.depart_iso}T20:05:00Z | 0 | Y9 B7 M4 | $450.00 USD | [Book BA178](https://reservations.amadeus.internal/pnr/create?flt=BA178&dt={spec.dates.depart_iso}) |\n"
        f"| VS0004 | Virgin Atlantic | A350-1000 | {spec.dates.depart_iso}T18:30:00Z | {spec.dates.depart_iso}T06:20:00Z | 0 | Y4 B2 M0 | $482.50 USD | [Book VS004](https://reservations.amadeus.internal/pnr/create?flt=VS004&dt={spec.dates.depart_iso}) |\n"
        f"| UA0904 | United Airlines | 767-400ER | {spec.dates.depart_iso}T21:40:00Z | {spec.dates.depart_iso}T09:45:00Z | 0 | Y8 B5 M2 | $515.00 USD | [Book UA904](https://reservations.amadeus.internal/pnr/create?flt=UA904&dt={spec.dates.depart_iso}) |\n\n"
        "Notice: Fare rules indicate non-refundable status. For passenger name record modifications, "
        "submit IATA standard Form 7401-B to the global consolidation desk."
    )
    return response


# -----------------------------------------------------------------------------
# Registration Helper
# -----------------------------------------------------------------------------

def register_flawed_tools(server: MCPServer) -> None:
    """Register all flawed reference tools onto the given MCPServer."""
    server.tool(name="fetch_meteorological_telemetry_v2")(fetch_meteorological_telemetry_v2)
    server.tool(name="execute_home_iot_command_rpc")(execute_home_iot_command_rpc)
    server.tool(name="query_itinerary_and_schedule_matrix")(query_itinerary_and_schedule_matrix)
