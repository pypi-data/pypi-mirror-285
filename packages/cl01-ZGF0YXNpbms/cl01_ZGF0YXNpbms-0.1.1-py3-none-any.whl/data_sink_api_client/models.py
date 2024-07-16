from pydantic import BaseModel, Field
from typing import Optional, Any, Literal, Union, List
from uuid import UUID
from enum import Enum


class CollectionStatus(str, Enum):
  UNDEFINED: str = 'undefined'  # undefined
  CREATED: str = 'created'  # created
  READY: str = 'ready'  # ready
  DELETED: str = 'deleted'  # deleted
  ERROR: str = 'error'  # error


class CollectionType(str, Enum):
  QDRANT: str = 'qdrant'  # qdrant
  UNKNOWN: str = 'unknown'  # unknown


class DistanceMethod(str, Enum):
  COSINE: str = 'Cosine'  # Cosine
  EUCLIDEAN: str = 'Euclidean'  # Euclidean
  DOT: str = 'Dot'  # Dot
  MANHATTAN: str = 'Manhattan'  # Manhattan


class CollectionEntity(BaseModel):
  input: str = ...  # Input
  payload: dict = ...  # Payload
  id: Union[UUID, str, int] = ...  # Id


class CollectionEntityAlreadyExistsResponse(BaseModel):
  detail: str = 'Collection entity with this id already exists'  # Detail


class CollectionEntityListResponse(BaseModel):
  results: List['CollectionEntityResponse'] = ...  # Results
  count: int = ...  # Count


class CollectionEntityResponse(BaseModel):
  id: Union[UUID, str, int] = ...  # Id
  payload: dict = ...  # Payload


class CollectionInfo(BaseModel):
  id: Union[UUID, str, int, Any] = None  # Id
  name: str = ...  # Name
  embedding_model: 'EmbeddingModel' = ...
  collection_id: Union[UUID, Any] = None  # Collection Id
  metadata: Union[dict, 'QdrantCollectionMetadata'] = None  # Metadata
  owner: Union[str, Any] = None  # Owner
  collection_type: CollectionType = CollectionType.QDRANT  # CollectionType
  status: CollectionStatus = CollectionStatus.UNDEFINED  # CollectionStatus


class CollectionNotFoundResponse(BaseModel):
  detail: str = 'Collection not found'  # Detail


class CollectionOrCollectionEntityNotFoundResponse(BaseModel):
  detail: str = 'Collection or collection entity not found'  # Detail


class DataPoint(BaseModel):
  input: str = ...  # Input
  payload: dict = ...  # Payload
  id: Union[UUID, str, int] = None  # Id


class EmbeddingModel(BaseModel):
  id: Union[UUID, str, int] = None  # Id
  name: str = ...  # Name
  version: str = '0.0.1'  # Version
  library: str = 'transformers'  # Library
  loaded: bool = False  # Loaded
  eb_model: Any = None  # Eb Model
  tokenizer: Any = None  # Tokenizer


class EmbeddingRequest(BaseModel):
  text: Union[List[str], str] = ...  # Text
  eb_model_name: str = ...  # Eb Model Name
  eb_model_version: Union[str, Any] = None  # Eb Model Version


class EmbeddingResponse(BaseModel):
  embeddings: 'Embeddings' = ...  # Embeddings
  eb_model_name: str = ...  # Eb Model Name
  eb_model_version: Union[str, Any] = None  # Eb Model Version


class HTTPValidationError(BaseModel):
  detail: List['ValidationError'] = None  # Detail


class HealthCheckResponse(BaseModel):
  status: str = 'ok'  # Status


class ModelNotFoundResponse(BaseModel):
  detail: str = 'Model not found'  # Detail


class PartialCollectionInfo(BaseModel):
  id: Union[UUID, str, int, Any] = None  # Id
  name: Union[str, Any] = None  # Name
  embedding_model: Union['PartialEmbeddingModel', Any] = None
  collection_id: Union[UUID, Any] = None  # Collection Id
  metadata: Union[dict, 'QdrantCollectionMetadata', Any] = None  # Metadata
  owner: Union[str, Any] = None  # Owner
  collection_type: Union['CollectionType', Any] = None
  status: Union['CollectionStatus', Any] = None


class PartialEmbeddingModel(BaseModel):
  id: Union[UUID, str, int, Any] = None  # Id
  name: Union[str, Any] = None  # Name
  version: Union[str, Any] = None  # Version
  library: Union[str, Any] = None  # Library
  loaded: Union[bool, Any] = None  # Loaded
  eb_model: Any = None  # Eb Model
  tokenizer: Any = None  # Tokenizer


class QdrantCollectionInfo(BaseModel):
  id: Union[UUID, str, int, Any] = None  # Id
  name: str = ...  # Name
  embedding_model: 'EmbeddingModel' = ...
  collection_id: Union[UUID, Any] = None  # Collection Id
  metadata: 'QdrantCollectionMetadata' = ...
  owner: Union[str, Any] = None  # Owner
  collection_type: CollectionType = CollectionType.QDRANT  # CollectionType
  status: CollectionStatus = CollectionStatus.UNDEFINED  # CollectionStatus


class QdrantCollectionMetadata(BaseModel):
  host: str = ...  # Host
  token: str = ...  # Token
  distance_method: DistanceMethod = DistanceMethod.DOT  # DistanceMethod
  dimension: Union[int, Any] = None  # Dimension


class QdrantCredentialsInvalid(BaseModel):
  detail: str = 'Qdrant credentials invalid'  # Detail


class QueryRequest(BaseModel):
  query: str = ...  # Query
  top_k: Union[int, Any] = 10  # Top K


class ReadRootResponse(BaseModel):
  status: str = 'ok'  # Status


class UnsupportedCollectionTypeResponse(BaseModel):
  detail: str = 'Unsupported collection type'  # Detail


class ValidationError(BaseModel):
  loc: List[Union[str, int]] = ...  # Location
  msg: str = ...  # Message
  type: str = ...  # Error Type

