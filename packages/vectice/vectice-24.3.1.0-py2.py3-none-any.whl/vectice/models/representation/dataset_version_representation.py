from __future__ import annotations

from functools import reduce
import logging
from typing import TYPE_CHECKING, Any, Dict

from hurry.filesize import size

from vectice.api.json.dataset_version_representation import DatasetVersionRepresentationOutput
from vectice.models.attachment import TAttachment
from vectice.models.attachment_container import AttachmentContainer
from vectice.models.property import Property
from vectice.models.representation.dataset_representation import DatasetRepresentation
from vectice.utils.common_utils import (
    flatten_resources,
    format_attachments,
    format_properties,
    repr_class,
    strip_dict_list,
)
from vectice.utils.dataframe_utils import repr_list_as_pd_dataframe

if TYPE_CHECKING:
    from pandas import DataFrame

    from vectice.api.client import Client


_logger = logging.getLogger(__name__)


class DatasetVersionRepresentation:
    """Represents the metadata of a Vectice dataset version.

    A Dataset Version Representation shows information about a specific version of a dataset from the Vectice app. It makes it easier to get and read this information through the API.

    NOTE: **Hint**
        A dataset version ID starts with 'DTV-XXX'. Retrieve the ID in the Vectice App, then use the ID with the following methods to get the dataset version:
        ```connect.dataset_version('DTV-XXX')``` or ```connect.browse('DTV-XXX')```
        (see [Connection page](https://api-docs.vectice.com/reference/vectice/connection/#vectice.Connection.dataset_version)).

    Attributes:
        id (str): The unique identifier of the dataset version.
        project_id (str): The identifier of the project to which the dataset version belongs.
        name (str): The name of the dataset version. For dataset versions it corresponds to the version number.
        description (str): The description of the dataset version.
        properties (List[Dict[str, Any]]): The properties associated with the dataset version.
        resources (List[Dict[str, Any]]): The resources summary with the type, number of files and aggregated total number of columns for each resource inside the dataset version.
        dataset_representation (DatasetRepresentation): Holds informations about the source dataset linked to the dataset version, where all versions are grouped together.
    """

    def __init__(self, output: DatasetVersionRepresentationOutput, client: Client):
        self.id = output.id
        self.project_id = output.project_id
        self.name = output.name
        self.description = output.description
        self.properties = strip_dict_list(output.properties)
        self.resources = output.resources
        self.dataset_representation = DatasetRepresentation(output.dataset, client)
        self._client = client
        self._output = output

    def __repr__(self):
        return repr_class(self)

    def asdict(self) -> Dict[str, Any]:
        """Transform the DatasetVersionRepresentation into a organised dictionary.

        Returns:
            The object represented as a dictionary
        """
        flat_properties = {prop["key"]: prop["value"] for prop in self.properties}
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "properties": flat_properties,
            "resources": flatten_resources(self.resources),
            "dataset_representation": (
                self.dataset_representation._asdict()  # pyright: ignore reportPrivateUsage
                if self.dataset_representation
                else None
            ),
        }

    def properties_as_dataframe(self) -> DataFrame:
        """Transforms the properties of the DatasetVersionRepresentation into a DataFrame for better readability.

        Returns:
            A pandas DataFrame containing the properties of the dataset version.
        """
        return repr_list_as_pd_dataframe(self.properties)

    def resources_as_dataframe(self) -> DataFrame:
        """Transforms the resources of the DatasetVersionRepresentation into a DataFrame for better readability.

        Returns:
            A pandas DataFrame containing the resources of the dataset version.
        """
        return repr_list_as_pd_dataframe(
            reduce(
                lambda acc, res: [*acc, {**res, "size": size(int(res["size"])) if res["size"] is not None else None}],
                self.resources,
                [],
            )
        )

    def update(
        self,
        properties: dict[str, str | int] | list[Property] | Property | None = None,
        attachments: str | list[str] | None = None,
        columns_description: dict[str, str] | str | None = None,
    ) -> None:
        """Update the Dataset Version from the API.

        Parameters:
            properties: The new properties of the dataset.
            attachments: The new attachments of the dataset.
            columns_description: A dictionary or path to a csv file to map the column's name to a specific description. Should follow the format { "column_name": "Description", ... }

        Returns:
            None
        """
        if properties is not None:
            self._upsert_properties(properties)

        if attachments is not None:
            self._update_attachments(attachments)

        if columns_description is not None:
            self._update_dataset_version(columns_description)

    def _upsert_properties(self, properties: dict[str, str | int] | list[Property] | Property):
        clean_properties = list(map(lambda property: property.key_val_dict(), format_properties(properties)))
        new_properties = self._client.upsert_properties("dataSetVersion", self.id, clean_properties)
        self.properties = strip_dict_list(new_properties)
        _logger.info(f"Dataset version {self.id!r} properties successfully updated.")

    def _update_attachments(self, attachments: TAttachment):
        container = AttachmentContainer(self._output, self._client)
        container.upsert_attachments(format_attachments(attachments))
        _logger.info(f"Dataset version {self.id!r} attachments successfully updated.")

    def _update_dataset_version(self, columns_description: dict[str, str] | str):
        if isinstance(columns_description, str):
            self._client.update_columns_description_via_csv(self.id, columns_description)
        else:
            items = columns_description.items()
            list_columns_description = list(map(lambda x: {"name": x[0], "description": x[1]}, items))
            self._client.update_dataset_version(self.id, list_columns_description)

        self._client.warn_if_dataset_version_columns_are_missing_description(self.id)
        _logger.info(f"Dataset version {self.id!r} columns descriptions successfully updated.")
