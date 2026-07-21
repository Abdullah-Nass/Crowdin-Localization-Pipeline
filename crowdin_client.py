from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Iterable
from time import sleep
import dotenv
from crowdin_api import CrowdinClient
import requests
import zipfile
dotenv.load_dotenv()


class Crowdin:
    """Small convenience wrapper around the official Crowdin Python SDK."""

    def __init__(self, token: str | None = None, project_id: int | None = None) -> None:
        self.token = token or os.getenv("TOKEN")
        if not self.token:
            raise ValueError("Crowdin API token is required.")

        env_project_id = os.getenv("PROJECT_ID")
        self.project_id = project_id or (int(env_project_id) if env_project_id else None)
        self.client = CrowdinClient(token=self.token)

    @staticmethod
    def _unwrap_data(response: dict[str, Any]) -> Any:
        return response.get("data", response)

    def _resolve_project_id(self, project_id: int | None = None) -> int:
        resolved_project_id = project_id or self.project_id
        if resolved_project_id is None:
            raise ValueError("project_id is required. Pass it to this method or set PROJECT_ID in .env.")
        return resolved_project_id

    def get_projects(self, limit: int | None = None) -> list[dict[str, Any]]:
        """Return projects visible to the configured Crowdin token."""
        return self._unwrap_data(self.client.projects.list_projects(limit=limit)) # type: ignore

    def get_project(self, project_id: int | None = None) -> dict[str, Any]:
        """Return one project by id."""
        return self._unwrap_data(
            self.client.projects.get_project(projectId=self._resolve_project_id(project_id)) # type: ignore
        )

    def get_files(
        self,
        project_id: int | None = None,
        branch_id: int | None = None,
        directory_id: int | None = None,
        recursion: bool | None = True,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Return source files for a project."""
        return self._unwrap_data(
                self.client.source_files.list_files(
                projectId=self._resolve_project_id(project_id),
                branchId=branch_id,
                directoryId=directory_id,
                recursion=recursion,
                limit=limit,
            ) # type: ignore
        )

    def get_progress(
        self,
        project_id: int | None = None,
        language_ids: Iterable[str] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Return translation progress for a project."""
        return self._unwrap_data(
            self.client.translation_status.get_project_progress(
                projectId=self._resolve_project_id(project_id),
                languageIds=language_ids,
                limit=limit,
            ) # type: ignore
        )

    def build_translation(
        self,
        project_id: int | None = None,
        *,
        target_language_ids: Iterable[str] | None = None,
        skip_untranslated_strings: bool = False,
        skip_untranslated_files: bool = False,
    ) -> dict[str, Any]:
        """Start a translation build and return the created build data."""
        request_data: dict[str, Any] = {
            "skipUntranslatedStrings": skip_untranslated_strings,
            "skipUntranslatedFiles": skip_untranslated_files,
        }
        if target_language_ids:
            request_data["targetLanguageIds"] = list(target_language_ids)

        return self._unwrap_data(
            self.client.translations.build_project_translation(
                request_data=request_data,
                projectId=self._resolve_project_id(project_id),
            ) # type: ignore
        )

    def get_build_status(self, build_id: int, project_id: int | None = None) -> dict[str, Any]:
        """Return the current status for a translation build."""
        return self._unwrap_data(
            self.client.translations.check_project_build_status(
                buildId=build_id,
                projectId=self._resolve_project_id(project_id),
            ) # type: ignore
        )

    def download_build(self, build_id: int, project_id: int | None = None) -> dict[str, Any]:
        """Return the download URL for a completed translation build."""
        return self._unwrap_data(
            self.client.translations.download_project_translations(
                buildId=build_id,
                projectId=self._resolve_project_id(project_id),
            ) # type: ignore
        )

    def upload_file(
        self,
        file_path: str | Path,
        project_id: int | None = None,
        *,
        name: str | None = None,
        branch_id: int | None = None,
        directory_id: int | None = None,
    ) -> dict[str, Any]:
        """Upload a local source file to Crowdin and add it to the project."""
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File does not exist: {path}")

        with path.open("rb") as file:
            storage = self._unwrap_data(self.client.storages.add_storage(file=file)) # type: ignore

        return self._unwrap_data(
            self.client.source_files.add_file(
                storageId=storage["id"],
                name=name or path.name,
                projectId=self._resolve_project_id(project_id),
                branchId=branch_id,
                directoryId=directory_id,
            ) # type: ignore
        )
