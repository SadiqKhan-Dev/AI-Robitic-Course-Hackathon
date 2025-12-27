#!/usr/bin/env python3
"""Validate embedding output."""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def validate_embeddings(
    input_file: str = "./data/embeddings.jsonl",
    expected_dimensions: int = 1024,
):
    """Validate embedding output.

    Args:
        input_file: Path to embeddings JSONL file
        expected_dimensions: Expected embedding dimensions

    Returns:
        Tuple of (is_valid, stats_dict)
    """
    embeddings_path = Path(input_file)
    stats = {
        "total_embeddings": 0,
        "valid_embeddings": 0,
        "wrong_dimensions": 0,
        "missing_metadata": 0,
        "duplicate_ids": 0,
        "errors": [],
    }

    if not embeddings_path.exists():
        return False, {**stats, "errors": ["Embeddings file does not exist"]}

    seen_ids = set()
    chunk_ids = set()

    with embeddings_path.open("r") as f:
        for line_num, line in enumerate(f, 1):
            try:
                record = json.loads(line.strip())
                stats["total_embeddings"] += 1

                # Check required fields
                if "chunk_id" not in record:
                    stats["missing_metadata"] += 1
                    stats["errors"].append(f"Line {line_num}: Missing chunk_id")
                    continue

                if "vector" not in record:
                    stats["missing_metadata"] += 1
                    stats["errors"].append(f"Line {line_num}: Missing vector")
                    continue

                chunk_id = record["chunk_id"]

                # Check for duplicates
                if chunk_id in seen_ids:
                    stats["duplicate_ids"] += 1
                    stats["errors"].append(f"Line {line_num}: Duplicate chunk_id {chunk_id}")
                seen_ids.add(chunk_id)
                chunk_ids.add(chunk_id)

                # Check dimensions
                vector = record["vector"]
                if len(vector) != expected_dimensions:
                    stats["wrong_dimensions"] += 1
                    stats["errors"].append(
                        f"Line {line_num}: Wrong dimensions {len(vector)} != {expected_dimensions}"
                    )
                    continue

                # Check metadata
                required_fields = ["url", "title", "chunk_index", "total_chunks", "token_count"]
                for field in required_fields:
                    if field not in record.get("metadata", {}):
                        stats["missing_metadata"] += 1
                        stats["errors"].append(
                            f"Line {line_num}: Missing metadata field {field}"
                        )
                        break

                stats["valid_embeddings"] += 1

            except json.JSONDecodeError as e:
                stats["errors"].append(f"Line {line_num}: Invalid JSON - {e}")

    is_valid = (
        stats["total_embeddings"] > 0 and
        stats["valid_embeddings"] == stats["total_embeddings"] and
        stats["wrong_dimensions"] == 0 and
        stats["duplicate_ids"] == 0
    )

    return is_valid, stats


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate embedding output")
    parser.add_argument(
        "--input",
        default="./data/embeddings.jsonl",
        help="Path to embeddings JSONL file",
    )
    parser.add_argument(
        "--dimensions",
        type=int,
        default=1024,
        help="Expected embedding dimensions",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON format",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = main()

    is_valid, stats = validate_embeddings(args.input, args.dimensions)

    if args.json:
        print(json.dumps({"valid": is_valid, **stats}))
    else:
        print("\n" + "=" * 50)
        print("Embedding Validation Results")
        print("=" * 50)
        print(f"  Total Embeddings:  {stats['total_embeddings']}")
        print(f"  Valid Embeddings:  {stats['valid_embeddings']}")
        print(f"  Wrong Dimensions:  {stats['wrong_dimensions']}")
        print(f"  Duplicate IDs:     {stats['duplicate_ids']}")
        print(f"  Missing Metadata:  {stats['missing_metadata']}")
        print("=" * 50)

        if stats["errors"]:
            print("\nErrors:")
            for error in stats["errors"][:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(stats["errors"]) > 10:
                print(f"  ... and {len(stats['errors']) - 10} more")
            print()

        if is_valid:
            print("Status: VALID")
            sys.exit(0)
        else:
            print("Status: INVALID")
            sys.exit(1)
