from io import IOBase
from typing import Self, Any, Iterable, AsyncIterable

import httpx
from httpx import URL

from pinexq_client.core import Link, MediaTypes
from pinexq_client.core.hco.upload_action_hco import UploadParameters
from pinexq_client.job_management.enterjma import enter_jma
from pinexq_client.job_management.hcos import WorkDataLink, WorkDataRootHco, WorkDataHco
from pinexq_client.job_management.hcos.entrypoint_hco import EntryPointHco
from pinexq_client.job_management.known_relations import Relations
from pinexq_client.job_management.model import SetTagsWorkDataParameters


class WorkData:
    """Convenience wrapper for handling WorkDataHcos in the JobManagement-Api.
    """

    _client: httpx.Client
    _entrypoint: EntryPointHco
    _work_data_root: WorkDataRootHco
    _work_data: WorkDataHco | None = None

    def __init__(self, client: httpx.Client):
        """

        Args:
            client: An httpx.Client instance initialized with the api-host-url as `base_url`
        """
        self._client = client
        self._entrypoint = enter_jma(client)
        self._work_data_root = self._entrypoint.work_data_root_link.navigate()

    def create(
            self,
            *,
            filename: str,
            mediatype: str = MediaTypes.OCTET_STREAM,
            json: Any | None = None,
            file: IOBase | None = None,
            binary: str | bytes | Iterable[bytes] | AsyncIterable[bytes] | None = None
    ) -> Self:
        work_data_link = self._work_data_root.upload_action.execute(
            UploadParameters(
                filename=filename, binary=binary, json=json, file=file, mediatype=mediatype
            )
        )
        self._get_by_link(work_data_link)
        return self

    def _get_by_link(self, processing_step_link: WorkDataLink):
        self._work_data = processing_step_link.navigate()

    @classmethod
    def from_hco(cls, client: httpx.Client, work_data: WorkDataHco) -> Self:
        """Initializes a `WorkData` object from an existing WorkDataHco object.

        Args:
            client: An httpx.Client instance initialized with the api-host-url as `base_url`
            work_data: The WorkDataHco to initialize this WorkData from.

        Returns:
            The newly created work data as `WorkData` object.
        """

        work_data_instance = cls(client)
        work_data_instance._work_data = work_data
        return work_data_instance

    @classmethod
    def from_url(cls, client: httpx.Client, work_data_url: URL) -> Self:
        """Initializes a `WorkData` object from an existing work data given by its link as URL.

        Args:
            client: An httpx.Client instance initialized with the api-host-url as `base_url`
            work_data_url: The URL of the work data

        Returns:
            The newly created work data as `WorkData` object
        """
        link = Link.from_url(
            work_data_url,
            [str(Relations.CREATED_RESSOURCE)],
            "Uploaded work data",
            MediaTypes.SIREN,
        )
        processing_step_instance = cls(client)
        processing_step_instance._get_by_link(WorkDataLink.from_link(client, link))
        return processing_step_instance

    def refresh(self) -> Self:
        """Updates the work data from the server

        Returns:
            This `WorkData` object, but with updated properties.
        """
        self._work_data = self._work_data.self_link.navigate()
        return self

    def set_tags(self, tags: list[str]):
        """Set tags to the processing step.

        Returns:
            This `WorkData` object"""
        self._work_data.edit_tags_action.execute(SetTagsWorkDataParameters(
            tags=tags
        ))
        self.refresh()
        return self

    def allow_deletion(self) -> Self:
        """Allow deletion.

        Returns:
            This `WorkData` object"""
        self._work_data.allow_deletion_action.execute()
        self.refresh()
        return self

    def disallow_deletion(self) -> Self:
        """Disallow deletion.

        Returns:
            This `WorkData` object"""
        self._work_data.disallow_deletion_action.execute()
        self.refresh()
        return self

    def hide(self) -> Self:
        """Hide WorkData.

        Returns:
            This `WorkData` object"""
        self._work_data.hide_action.execute()
        self.refresh()
        return self

    def delete(self) -> Self:
        """Delete WorkData.

        Returns:
            This `WorkData` object"""
        self._work_data.delete_action.execute()
        return self

    def download(self) -> bytes:
        """Download WorkData.

        Returns:
            Downloaded WorkData in bytes
        """
        return self._work_data.download_link.download()

    def self_link(self) -> WorkDataLink:
        return self._work_data.self_link
