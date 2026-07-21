# Crowdin API Client

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

To enable the pipeline, add these secrets to your GitHub repo:  
**Settings → Secrets and variables → Actions**

| Secret               | Value                   |
| -------------------- | ----------------------- |
| `CROWDIN_TOKEN`      | Your Crowdin API token  |
| `CROWDIN_PROJECT_ID` | Your Crowdin project ID |

---

## Project Structure

```
├── .github/workflows/    # CI/CD pipeline
├── demo_assets/          # Sample source file for upload demo
├── scripts/              # CI health check script
├── crowdin_client.py     # Crowdin API wrapper
├── demo.py               # End-to-end workflow demo
└── requirements.txt
```
