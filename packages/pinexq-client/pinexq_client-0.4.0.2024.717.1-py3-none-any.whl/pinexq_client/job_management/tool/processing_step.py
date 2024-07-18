from typing import Any, Self

import httpx
from httpx import URL

from pinexq_client.core import Link, MediaTypes
from pinexq_client.core.hco.upload_action_hco import UploadParameters
from pinexq_client.job_management.enterjma import enter_jma
from pinexq_client.job_management.hcos import ProcessingStepHco, ProcessingStepLink
from pinexq_client.job_management.hcos.entrypoint_hco import EntryPointHco
from pinexq_client.job_management.hcos.job_hco import GenericProcessingConfigureParameters
from pinexq_client.job_management.hcos.processingsteproot_hco import ProcessingStepsRootHco
from pinexq_client.job_management.known_relations import Relations
from pinexq_client.job_management.model import (
    CreateProcessingStepParameters,
    EditProcessingStepParameters,
    SetProcessingStepTagsParameters,
)


class ProcessingStep:
    """Convenience wrapper for handling ProcessingStepHcos in the JobManagement-Api.
    """

    _client: httpx.Client
    _entrypoint: EntryPointHco
    _processing_steps_root: ProcessingStepsRootHco
    _processing_step: ProcessingStepHco | None = None

    def __init__(self, client: httpx.Client):
        """

        Args:
            client: An httpx.Client instance initialized with the api-host-url as `base_url`
        """
        self._client = client
        self._entrypoint = enter_jma(client)
        self._processing_steps_root = self._entrypoint.processing_step_root_link.navigate()

    def create(self, title: str, function_name: str) -> Self:
        """
        Creates a new ProcessingStep by name.

        Args:
            title: Title of the ProcessingStep to be created
            function_name: Function name of the ProcessingStep to be created

        Returns:
            The newly created ProcessingStep as `ProcessingStep` object
        """
        processing_step_hco = self._processing_steps_root.register_new_action.execute(CreateProcessingStepParameters(
            title=title,
            function_name=function_name
        ))
        self._processing_step = processing_step_hco
        return self

    def _get_by_link(self, processing_step_link: ProcessingStepLink):
        self._processing_step = processing_step_link.navigate()

    @classmethod
    def from_hco(cls, client: httpx.Client, processing_step: ProcessingStepHco) -> Self:
        """Initializes a `ProcessingStep` object from an existing ProcessingStepHco object.

        Args:
            client: An httpx.Client instance initialized with the api-host-url as `base_url`
            processing_step: The 'ProcessingStepHco' to initialize this ProcessingStep from.

        Returns:
            The newly created processing step as `ProcessingStep` object.
        """
        processing_step_instance = cls(client)
        processing_step_instance._processing_step = processing_step
        return processing_step_instance

    @classmethod
    def from_url(cls, client: httpx.Client, processing_step_url: URL) -> Self:
        """Initializes a `ProcessingStep` object from an existing processing step given by its link as URL.

        Args:
            client: An httpx.Client instance initialized with the api-host-url as `base_url`
            processing_step_url: The URL of the processing step

        Returns:
            The newly created processing step as `ProcessingStep` object
        """
        link = Link.from_url(
            processing_step_url,
            [str(Relations.CREATED_RESSOURCE)],
            "Created processing step",
            MediaTypes.SIREN,
        )
        processing_step_instance = cls(client)
        processing_step_instance._get_by_link(ProcessingStepLink.from_link(client, link))
        return processing_step_instance

    def refresh(self) -> Self:
        """Updates the processing step from the server

        Returns:
            This `ProcessingStep` object, but with updated properties.
        """
        self._processing_step = self._processing_step.self_link.navigate()
        return self

    def set_tags(self, tags: list[str]) -> Self:
        """Set tags to the processing step.

        Returns:
            This `ProcessingStep` object"""
        self._processing_step.edit_tags_action.execute(SetProcessingStepTagsParameters(
            tags=tags
        ))
        self.refresh()
        return self

    def edit_properties(
            self,
            *,
            new_title: str | None = None,
            new_function_name: str | None = None,
            is_public: bool | None = None
    ) -> Self:
        """Edit processing step properties.

        Returns:
            This `ProcessingStep` object"""
        self._processing_step.edit_properties_action.execute(EditProcessingStepParameters(
            title=new_title,
            function_name=new_function_name,
            is_public=is_public
        ))
        self.refresh()
        return self

    def configure_default_parameters(self, **parameters: Any) -> Self:
        """Set the parameters to run the processing step with.

        Args:
            **parameters: Any keyword parameters provided will be forwarded as parameters
                to the processing step function.

        Returns:
            This `ProcessingStep` object
        """
        self._processing_step.configure_default_parameters_action.execute(
            GenericProcessingConfigureParameters.model_validate(parameters)
        )

        self.refresh()
        return self

    def clear_default_parameters(self) -> Self:
        """Clear default parameters.

        Returns:
            This `ProcessingStep` object
        """
        self._processing_step.clear_default_parameters_action.execute()
        self.refresh()

        return self

    def upload_configuration(self, json_data: Any) -> Self:
        """Upload processing configuration.

        Returns:
            This `ProcessingStep` object
        """
        self._processing_step.upload_configuration_action.execute(
            UploadParameters(
                filename="config.json",  # placeholder, jma does not care about filename
                mediatype=MediaTypes.APPLICATION_JSON,
                json=json_data
            )
        )
        self.refresh()

        return self

    def self_link(self) -> ProcessingStepLink:
        return self._processing_step.self_link
