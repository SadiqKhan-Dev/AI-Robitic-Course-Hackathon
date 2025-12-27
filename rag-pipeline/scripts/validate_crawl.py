#!/usr/bin/env python3
"""Validate crawl output and extracted content."""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def validate_crawl(output_dir: str = "./data/cache/extracted", min_text_length: int = 50):
    """Validate crawl output.

    Args:
        output_dir: Directory containing extracted content
        min_text_length: Minimum expected text length per page

    Returns:
        Tuple of (is_valid, stats_dict)
    """
    cache_dir = Path(output_dir)
    stats = {
        "total_pages": 0,
        "valid_pages": 0,
        "missing_metadata": 0,
        "too_short": 0,
        "missing_fields": 0,
        "errors": [],
    }

    if not cache_dir.exists():
        return False, {**stats, "errors": ["Cache directory does not exist"]}

    # Find all text files (metadata files have .meta.json extension)
    text_files = list(cache_dir.glob("*.txt"))
    stats["total_pages"] = len(text_files)

    for text_path in text_files:
        url_hash = text_path.stem
        meta_path = text_path.with_suffix(".meta.json")

        # Check metadata file exists
        if not meta_path.exists():
            stats["missing_metadata"] += 1
            stats["errors"].append(f"Missing metadata: {url_hash}")
            continue

        # Read content
        text_content = text_path.read_text()
        try:
            metadata = json.loads(meta_path.read_text())
        except json.JSONDecodeError as e:
            stats["missing_fields"] += 1
            stats["errors"].append(f"Invalid metadata JSON: {url_hash} - {e}")
            continue

        # Validate required fields
        required_fields = ["url", "title", "crawled_at", "content_hash"]
        missing = [f for f in required_fields if f not in metadata]
        if missing:
            stats["missing_fields"] += 1
            stats["errors"].append(f"Missing fields in {url_hash}: {missing}")
            continue

        # Validate text length
        if len(text_content.strip()) < min_text_length:
            stats["too_short"] += 1
            stats["errors"].append(f"Text too short ({len(text_content)} chars): {url_hash}")
            continue

        stats["valid_pages"] += 1

    is_valid = (
        stats["total_pages"] > 0 and
        stats["valid_pages"] == stats["total_pages"] and
        stats["missing_metadata"] == 0 and
        stats["missing_fields"] == 0 and
        stats["too_short"] == 0
    )

    return is_valid, stats


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate crawl output")
    parser.add_argument(
        "--output-dir",
        default="./data/cache/extracted",
        help="Directory containing extracted content",
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=50,
        help="Minimum expected text length per page",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON format",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = main()

    is_valid, stats = validate_crawl(args.output_dir, args.min_length)

    if args.json:
        print(json.dumps({"valid": is_valid, **stats}))
    else:
        print("\n" + "=" * 50)
        print("Crawl Validation Results")
        print("=" * 50)
        print(f"  Total Pages:  {stats['total_pages']}")
        print(f"  Valid Pages:  {stats['valid_pages']}")
        print(f"  Missing Meta: {stats['missing_metadata']}")
        print(f"  Too Short:    {stats['too_short']}")
        print(f"  Missing Fields: {stats['missing_fields']}")
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
