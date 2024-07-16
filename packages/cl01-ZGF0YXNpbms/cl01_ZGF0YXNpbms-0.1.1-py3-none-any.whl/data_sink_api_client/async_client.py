import httpx
from urllib.parse import urljoin
from pydantic import BaseModel
from . import models
from typing import List, Dict, Any, Optional, Union


class AsyncDatasinkAPIClient:
    def __init__(self, base_url, credentials, timeout=15):
        self.base_url = base_url
        self.credentials = credentials
        self.session = httpx.AsyncClient(headers={
            'Authorization': f'Basic {self.credentials}',
            'Content-Type': 'application/json'
        }, timeout=timeout)

    async def _request(self, method, endpoint, object_ctors, json_data=None, **kwargs):
        url = urljoin(self.base_url, endpoint)
        if json_data is not None:
            is_valid_list_payload = isinstance(json_data, list) and json_data
            if type(json_data.__class__) == type(BaseModel):
                json_data = json_data.model_dump()
            elif is_valid_list_payload and type(json_data[0].__class__) == type(BaseModel):
                json_data = [item.model_dump() for item in json_data]
            kwargs['json'] = json_data

        async with self.session:
            response = await self.session.request(method, url, **kwargs)

        object_ctor = object_ctors.get(response.status_code, dict)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return [object_ctor(**item) for item in data]
        return object_ctor(**data)

    async def read_root(self) -> models.ReadRootResponse:
        """Read Root"""
        return await self._request(
            'GET',
            '/',
            object_ctors={
                200: models.ReadRootResponse
            }
        )

    async def health_check(self) -> models.HealthCheckResponse:
        """Health Check"""
        return await self._request(
            'GET',
            '/health',
            object_ctors={
                200: models.HealthCheckResponse
            }
        )

    async def get_models(self) -> List[models.EmbeddingModel]:
        """Get Models"""
        return await self._request(
            'GET',
            '/models',
            object_ctors={
                200: models.EmbeddingModel
            }
        )

    async def create_model(self, embedding_model: models.EmbeddingModel) -> Union[models.HTTPValidationError, dict, models.EmbeddingModel]:
        """Create Model"""
        return await self._request(
            'POST',
            '/models',
            json_data=embedding_model,
            object_ctors={
                200: dict,
                201: models.EmbeddingModel,
                422: models.HTTPValidationError
            }
        )

    async def create_embedding(self, embedding_request: models.EmbeddingRequest) -> Union[models.HTTPValidationError, models.EmbeddingResponse, dict, models.ModelNotFoundResponse]:
        """Create Embedding"""
        return await self._request(
            'POST',
            '/embed',
            json_data=embedding_request,
            object_ctors={
                200: dict,
                201: models.EmbeddingResponse,
                404: models.ModelNotFoundResponse,
                422: models.HTTPValidationError
            }
        )

    async def get_collections(self) -> List[dict]:
        """Get Collections"""
        return await self._request(
            'GET',
            '/collections',
            object_ctors={
                200: dict
            }
        )

    async def create_collection(self, collection_info: Union['CollectionInfo', 'QdrantCollectionInfo']) -> Union[models.HTTPValidationError, dict, models.QdrantCollectionInfo, models.UnsupportedCollectionTypeResponse]:
        """Create Collection"""
        return await self._request(
            'POST',
            '/collections',
            json_data=collection_info,
            object_ctors={
                200: dict,
                201: models.QdrantCollectionInfo,
                400: models.UnsupportedCollectionTypeResponse,
                422: models.HTTPValidationError
            }
        )

    async def update_collection(self, collection_id, partial_collection_info: models.PartialCollectionInfo) -> Union[models.HTTPValidationError, dict, models.CollectionNotFoundResponse]:
        """Update Collection"""
        return await self._request(
            'PATCH',
            f'/collections/{collection_id}',
            json_data=partial_collection_info,
            object_ctors={
                200: dict,
                404: models.CollectionNotFoundResponse,
                400: dict,
                422: models.HTTPValidationError
            }
        )

    async def delete_collection(self, collection_id) -> Union[models.HTTPValidationError, dict, models.CollectionNotFoundResponse]:
        """Delete Collection"""
        return await self._request(
            'DELETE',
            f'/collections/{collection_id}',
            object_ctors={
                200: dict,
                204: dict,
                404: models.CollectionNotFoundResponse,
                422: models.HTTPValidationError
            }
        )

    async def get_collection(self, collection_id) -> Union[models.HTTPValidationError, dict, models.CollectionNotFoundResponse]:
        """Get Collection"""
        return await self._request(
            'GET',
            f'/collections/{collection_id}',
            object_ctors={
                200: dict,
                404: models.CollectionNotFoundResponse,
                422: models.HTTPValidationError
            }
        )

    async def query(self, collection_id, query_request: models.QueryRequest) -> Union[models.HTTPValidationError, dict, models.CollectionNotFoundResponse, models.UnsupportedCollectionTypeResponse]:
        """Query"""
        return await self._request(
            'POST',
            f'/collections/{collection_id}/query',
            json_data=query_request,
            object_ctors={
                200: dict,
                400: models.UnsupportedCollectionTypeResponse,
                404: models.CollectionNotFoundResponse,
                422: models.HTTPValidationError
            }
        )

    async def get_collection_entities_list(self, collection_id, limit, offset) -> Union[models.HTTPValidationError, models.CollectionNotFoundResponse, models.CollectionEntityListResponse]:
        """Get Collection Entities List"""
        return await self._request(
            'GET',
            f'/collections/{collection_id}/entities',
            params=dict(limit=limit, offset=offset),
            object_ctors={
                200: models.CollectionEntityListResponse,
                404: models.CollectionNotFoundResponse,
                422: models.HTTPValidationError
            }
        )

    async def create_collection_entity(self, collection_id, collection_entity: models.CollectionEntity) -> Union[dict, models.CollectionEntityResponse, models.CollectionNotFoundResponse, models.CollectionEntityAlreadyExistsResponse, models.HTTPValidationError]:
        """Create Collection Entity"""
        return await self._request(
            'POST',
            f'/collections/{collection_id}/entities',
            json_data=collection_entity,
            object_ctors={
                200: dict,
                201: models.CollectionEntityResponse,
                404: models.CollectionNotFoundResponse,
                409: models.CollectionEntityAlreadyExistsResponse,
                422: models.HTTPValidationError
            }
        )

    async def get_collection_entity(self, collection_id, entity_id) -> Union[models.HTTPValidationError, models.CollectionEntityResponse, models.CollectionOrCollectionEntityNotFoundResponse]:
        """Get Collection Entity"""
        return await self._request(
            'GET',
            f'/collections/{collection_id}/entities/{entity_id}',
            object_ctors={
                200: models.CollectionEntityResponse,
                404: models.CollectionOrCollectionEntityNotFoundResponse,
                422: models.HTTPValidationError
            }
        )

    async def update_collection_entity(self, collection_id, entity_id, collection_entity: models.CollectionEntity) -> Union[models.HTTPValidationError, models.CollectionEntityResponse, models.CollectionOrCollectionEntityNotFoundResponse]:
        """Update Collection Entity"""
        return await self._request(
            'PUT',
            f'/collections/{collection_id}/entities/{entity_id}',
            json_data=collection_entity,
            object_ctors={
                200: models.CollectionEntityResponse,
                404: models.CollectionOrCollectionEntityNotFoundResponse,
                422: models.HTTPValidationError
            }
        )

    async def delete_collection_entity(self, collection_id, entity_id) -> Union[models.HTTPValidationError, dict, models.CollectionNotFoundResponse]:
        """Delete Collection Entity"""
        return await self._request(
            'DELETE',
            f'/collections/{collection_id}/entities/{entity_id}',
            object_ctors={
                200: dict,
                204: dict,
                404: models.CollectionNotFoundResponse,
                422: models.HTTPValidationError
            }
        )

    async def add_data(self, collection_id, data_point: Union['DataPoint', List['DataPoint']]) -> Union[models.HTTPValidationError, dict, models.CollectionNotFoundResponse, models.UnsupportedCollectionTypeResponse]:
        """Add Data"""
        return await self._request(
            'POST',
            f'/collections/{collection_id}/data',
            json_data=data_point,
            object_ctors={
                200: dict,
                201: dict,
                404: models.CollectionNotFoundResponse,
                400: models.UnsupportedCollectionTypeResponse,
                422: models.HTTPValidationError
            }
        )
