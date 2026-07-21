# Crowdin-Localization-Pipeline

A Python wrapper around the [Crowdin Python SDK](https://github.com/crowdin/crowdin-api-client-python) that automates the full localization pipeline — from uploading source files to downloading finished translations.

---

## Why?

This project demonstrates how localization workflows can be automated using the Crowdin API. It serves as an example of integrating translation management into development pipelines with Python and GitHub Actions.

---

## Features

- Upload source files to a Crowdin project
- Monitor translation progress across languages
- Build and download translated assets automatically
- Validate localization health in CI/CD

---

## Repository Sync

The project is connected to Crowdin using the Crowdin GitHub integration.

- Source changes are synchronized from GitHub to Crowdin.
- Completed translations can be synchronized back to the repository.
- API automation complements the repository sync for tasks such as translation progress monitoring and build/download workflows.

---

## Usage

Run the full workflow demo:

```bash
python demo.py
```

This will:

1. Print project info and source files
2. Show translation progress per language
3. Upload `demo_assets/content_from_api.json` (if present)
4. Build translations and poll until complete
5. Download and extract the ZIP to `translations/`

---

## CI/CD

The GitHub Actions pipeline runs on every push and pull request:

| Job                 | What it does                                            |
| ------------------- | ------------------------------------------------------- |
| Lint                | Runs `ruff` to check code quality                       |
| Localization health | Fails the build if any language is below 80% translated |

---

## Project Structure

```
├── .github/workflows/    # CI/CD pipeline
├── demo_assets/          # Sample source file for upload demo
├── public/
│   └── content/
│       └── en/           # Source language files
├── scripts/              # CI health check script
├── crowdin_client.py     # Crowdin API wrapper
├── demo.py               # End-to-end workflow demo
└── requirements.txt
```
