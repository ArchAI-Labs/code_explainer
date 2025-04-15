import pytest
from unittest.mock import patch, MagicMock
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from crewai.memory.storage import ltm_sqlite_storage
from code_explainer.utils.storage_config import (  # Replace 'your_module' with the actual name of your file
    get_long_term_memory,
    get_short_term_memory,
    get_entity_memory,
)
from code_explainer.utils.storage_qdrant import QdrantStorage  # Ensure correct import
from qdrant_client import QdrantClient
import os

# Mocking the storage classes to avoid actual database interactions
@pytest.fixture
def mock_ltm_sqlite_storage():
    mock = MagicMock(spec=ltm_sqlite_storage.LTMSQLiteStorage)
    return mock

@pytest.fixture
def mock_qdrant_storage():
    mock = MagicMock(spec=QdrantStorage)
    mock.client = MagicMock(spec=QdrantClient)
    mock.client.collection_exists.return_value = True  # Assume collection exists for most tests
    mock.client.get_fastembed_vector_params.return_value = {"size": 384, "distance": "Cosine"}
    mock.client.get_fastembed_sparse_vector_params.return_value = {}
    return mock


def test_get_long_term_memory(mock_ltm_sqlite_storage):
    # Arrange
    expected_db_path = "./memory/long_term_memory_storage.db"
    ltm_sqlite_storage.LTMSQLiteStorage = mock_ltm_sqlite_storage

    # Act
    ltm = get_long_term_memory()

    # Assert
    assert isinstance(ltm, LongTermMemory)
    mock_ltm_sqlite_storage.assert_called_once_with(db_path=expected_db_path)
    assert ltm.storage == mock_ltm_sqlite_storage.return_value

@patch.dict(os.environ, {"QDRANT_MODE": "memory", "EMBEDDER": "BAAI/bge-base-en"})
def test_get_short_term_memory():

    # Act
    stm = get_short_term_memory()

    # Assert
    assert isinstance(stm, ShortTermMemory)

@patch.dict(os.environ, {"QDRANT_MODE": "memory", "EMBEDDER": "BAAI/bge-base-en"})
def test_get_entity_memory():

    # Act
    entity_memory = get_entity_memory()

    # Assert
    assert isinstance(entity_memory, EntityMemory)