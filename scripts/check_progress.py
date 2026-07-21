from __future__ import annotations

import argparse
import sys

from crowdin_client import Crowdin


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crowdin translation progress gate.")
    parser.add_argument(
        "--threshold",
        type=int,
        default=80,
        help="Minimum translation percentage required (default: 80)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    threshold = args.threshold

    print(f"── Localization Health Check (threshold: {threshold}%) ──\n")

    try:
        client = Crowdin()
        progress = client.get_progress()
    except ValueError as e:
        print(f" Configuration error: {e}")
        print("  Set CROWDIN_TOKEN and CROWDIN_PROJECT_ID as GitHub Actions secrets.")
        sys.exit(1)
    except Exception as e:
        print(f" Failed to fetch progress from Crowdin: {e}")
        sys.exit(1)

    failing: list[tuple[str, int]] = []

    for entry in progress:
        data = entry.get("data", entry)
        lang = data["languageId"]
        t_pct = data["translationProgress"]
        print(f"  {lang:<10} {t_pct:>3}%")
        if t_pct < threshold:
            failing.append((lang, t_pct))

    print()

    if failing:
        print(f" Build failed — {len(failing)} language(s) below {threshold}%:")
        for lang, pct in failing:
            print(f"    {lang}: {pct}%")
        sys.exit(1)

    print(f" All languages meet the {threshold}% threshold. Pipeline passed.")


if __name__ == "__main__":
    main()