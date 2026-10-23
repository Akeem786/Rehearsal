"""Command-line entry point for running the Rehearsal evaluation runner."""

import argparse
import asyncio
from rehearsal.client import MCPClientConnector
from rehearsal.runner import load_fixtures, run_evaluation


async def async_main() -> None:
    parser = argparse.ArgumentParser(description="Run Rehearsal voice evaluation suite on natural utterances.")
    parser.add_argument("--domain", choices=["weather", "smart_home", "travel"], default=None, help="Evaluate a specific domain.")
    parser.add_argument("--offline", action="store_true", help="Run without live MCP server tool execution.")
    parser.add_argument("--json", action="store_true", help="Output raw JSON report.")
    args = parser.parse_args()

    cases = load_fixtures(domain=args.domain)
    print(f"Loaded {len(cases)} test cases across {'all domains' if not args.domain else args.domain}...")

    if args.offline:
        report = await run_evaluation(cases)
    else:
        async with MCPClientConnector() as client:
            report = await run_evaluation(cases, connector=client)

    if args.json:
        print(report.to_json())
    else:
        print(report.to_terminal_summary())


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
