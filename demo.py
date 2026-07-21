from __future__ import annotations

import sys
import time
import zipfile
from pathlib import Path
import requests
from crowdin_client import Crowdin


POLL_INTERVAL = 3


def separator(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print("─" * 60)


def step_project_info(client: Crowdin) -> None:
    separator("Project info")
    project = client.get_project()
    print(f"  Name        : {project['name']}")
    print(f"  Source lang : {project['sourceLanguageId']}")
    target_ids = [lang["id"] for lang in project.get("targetLanguages", [])]
    print(f"  Target langs: {', '.join(target_ids) or '—'}")


def step_list_files(client: Crowdin) -> None:
    separator("Source files")
    files = client.get_files()
    if not files:
        print("  (no files found)")
        return
    for f in files:
        data = f.get("data", f)
        print(f"  [{data['id']}] {data['name']}")


def step_translation_progress(client: Crowdin) -> None:
    separator("Translation progress")
    progress = client.get_progress()
    for entry in progress:
        data = entry.get("data", entry)
        lang = data["languageId"]
        t_pct = data["translationProgress"]
        a_pct = data["approvalProgress"]
        print(f"  {lang:<10} translated: {t_pct:>3}%   approved: {a_pct:>3}%")


def step_upload_file(client: Crowdin, file_path: Path) -> dict:
    separator("Upload source file")
    print(f"  Uploading: {file_path}")
    result = client.upload_file(file_path)
    print(f"  Uploaded '{result['name']}' (file id: {result['id']})")
    return result


def step_build_and_download(client: Crowdin, output_dir: Path) -> None:
    separator("Build translations")
    build = client.build_translation()
    build_id = build["id"]
    print(f"  Build started (id: {build_id})")

    while True:
        time.sleep(POLL_INTERVAL)
        status_data = client.get_build_status(build_id)
        status = status_data["status"]
        progress = status_data.get("progress", "?")
        print(f"  … status: {status} ({progress}%)")

        if status == "finished":
            break
        if status == "failed":
            raise RuntimeError("Build failed. Check Crowdin project settings.")

    separator("Download & extract")
    url = client.download_build(build_id)["url"]
    print("  Download URL obtained.")

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    zip_path = Path("translations.zip")
    zip_path.write_bytes(response.content)

    output_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(output_dir)
    zip_path.unlink()

    files_only = [p for p in output_dir.rglob("*") if p.is_file()]
    print(f"  Extracted {len(files_only)} file(s) to '{output_dir}/'")
    for p in files_only:
        print(f"    {p.relative_to(output_dir)}")


def main() -> None:
    try:
        client = Crowdin()

        step_project_info(client)
        step_list_files(client)
        step_translation_progress(client)

        sample_file = Path("demo_assets/content_from_api.json")
        if sample_file.exists():
            step_upload_file(client, sample_file)
        else:
            print(f"\n  Skipping upload — '{sample_file}' not found.")
            print("     Add a source file there to test the upload step.")

        step_build_and_download(client, output_dir=Path("translations"))

        print("\n✓ Demo complete.\n")

    except ValueError as e:
        print(f"\n Configuration error: {e}")
        print("    Make sure TOKEN and PROJECT_ID are set in your .env file.")
        sys.exit(1)
    except RuntimeError as e:
        print(f"\n  {e}")
        sys.exit(1)
    except requests.HTTPError as e:
        print(f"\n  HTTP error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n  Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()