#!/usr/bin/env python3
"""
Script to generate mock property data
Usage: python scripts/generate_mock_data.py [--count 10000] [--output data/mock_properties.json]
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generators.mock_property_generator import MockPropertyGenerator


def main():
    """Generate mock property data"""
    parser = argparse.ArgumentParser(description="Generate mock property data")
    parser.add_argument(
        "--count",
        type=int,
        default=10000,
        help="Number of properties to generate (default: 10000)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/mock_properties.json",
        help="Output JSON file path (default: data/mock_properties.json)"
    )
    parser.add_argument(
        "--duckdb",
        type=str,
        default="data/properties.duckdb",
        help="DuckDB database path (default: data/properties.duckdb)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    parser.add_argument(
        "--no-json",
        action="store_true",
        help="Skip JSON output"
    )
    parser.add_argument(
        "--no-duckdb",
        action="store_true",
        help="Skip DuckDB output"
    )

    args = parser.parse_args()

    # Create generator
    print(f"Initializing generator with seed {args.seed}...")
    generator = MockPropertyGenerator(seed=args.seed)

    # Generate properties
    print(f"\nGenerating {args.count:,} mock properties...")
    properties = generator.generate_batch(args.count)

    # Save to JSON
    if not args.no_json:
        print(f"\nSaving to JSON: {args.output}")
        # Create directory if needed
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        generator.save_to_json(properties, args.output)

    # Save to DuckDB
    if not args.no_duckdb:
        print(f"\nSaving to DuckDB: {args.duckdb}")
        # Create directory if needed
        Path(args.duckdb).parent.mkdir(parents=True, exist_ok=True)
        generator.save_to_duckdb(properties, args.duckdb)

    # Print statistics
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print(f"Total properties: {len(properties):,}")
    print(f"Price range: ${min(p['price'] for p in properties):,} - ${max(p['price'] for p in properties):,}")
    print(f"Average price: ${sum(p['price'] for p in properties) // len(properties):,}")

    # Property type distribution
    types = {}
    for p in properties:
        pt = p['property_type']
        types[pt] = types.get(pt, 0) + 1

    print(f"\nProperty types:")
    for pt, count in sorted(types.items()):
        print(f"  {pt}: {count:,} ({count/len(properties)*100:.1f}%)")

    # State distribution
    states = {}
    for p in properties:
        st = p['state']
        states[st] = states.get(st, 0) + 1

    print(f"\nStates:")
    for st, count in sorted(states.items()):
        print(f"  {st}: {count:,} ({count/len(properties)*100:.1f}%)")

    print("\nDone!")


if __name__ == "__main__":
    main()
