import logging
from pydantic import BaseModel
from typing import List, Optional, Dict
from sws_api_client.sws_api_client import SwsApiClient
logger = logging.getLogger(__name__)

class Label(BaseModel):
    en: str

class Lifecycle(BaseModel):
    state: str
    type: str
    previousState: Optional[str]
    created: int
    lastModified: int
    lastModifiedBy: str

class Domain(BaseModel):
    id: str
    label: Label
    description: Dict

class Binding(BaseModel):
    joinColumn: str

class Dimension(BaseModel):
    id: str
    label: Label
    description: Dict
    sdmxName: str
    codelist: str
    roots: List[str]
    binding: Binding
    checkValidityPeriod: bool
    formulas: List
    type: str

class Dimensions(BaseModel):
    dimensions: List[Dimension]

class PivotingGrouped(BaseModel):
    id: str
    ascending: bool

class Pivoting(BaseModel):
    grouped: List[PivotingGrouped]
    row: PivotingGrouped
    cols: PivotingGrouped

class DatasetBinding(BaseModel):
    observationTable: str
    coordinateTable: str
    sessionObservationTable: str
    metadataTable: str
    metadataElementTable: str
    sessionMetadataTable: str
    sessionMetadataElementTable: str
    validationTable: str
    sessionValidationTable: str
    tagObservationTable: str
    tags: List

class Dataset(BaseModel):
    id: str
    label: Label
    description: Dict
    sdmxName: str
    lifecycle: Lifecycle
    domain: Domain
    dimensions: Dimensions
    flags: Dict
    rules: Dict
    pivoting: Pivoting
    pluginbar: Dict
    showEmptyRows: bool
    showRealCalc: bool
    useApproveCycle: bool
    binding: DatasetBinding

class Fingerprint(BaseModel):
    empty: bool
    sessions: int
    queries: int
    tags: int
    computationTags: int
    modules: int

class DataModel(BaseModel):
    dataset: Dataset
    fingerprint: Fingerprint

class Datasets:

    def __init__(self, sws_client: SwsApiClient) -> None:
        self.sws_client = sws_client

    def get_dataset_export_details(self, dataset_id: str) -> dict:

        url = f"/dataset/{dataset_id}/info"
        params = {"extended": "true"}

        response = self.sws_client.discoverable.get('session_api', url, params=params)

        return response
    
    def get_dataset_info(self, dataset_id: str) -> DataModel:

        url = f"/admin/dataset/{dataset_id}"

        response = self.sws_client.discoverable.get('is_api', url)

        return response

    def create_dataset(self, dataset: Dataset) -> DataModel:

        url = "/admin/dataset"

        response = self.sws_client.discoverable.post('is_api', url, data=dataset.dict())

        return response
    
    def clone_dataset(self, dataset_id: str, new_id: str) -> DataModel:

        dataset = self.get_dataset_info(dataset_id)
        dataset.dataset.id = new_id
        new_dataset = self.create_dataset(dataset.dataset)
        return new_dataset