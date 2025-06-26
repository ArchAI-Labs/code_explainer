from typing import Any, Dict, List, Optional
import os

from crewai.memory.storage.rag_storage import RAGStorage
from qdrant_client import QdrantClient

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="qdrant_client")


class QdrantStorage(RAGStorage):
    """
    Extends Storage to handle embeddings for memory entries using Qdrant.

    """

    def __init__(self, type, allow_reset=True, embedder_config=None, crew=None):
        super().__init__(type, allow_reset, embedder_config, crew)

    def search(
        self,
        query: str,
        limit: int = 3,
        filter: Optional[dict] = None,
        score_threshold: float = 0,
    ) -> List[Any]:
        points = self.client.query(
            self.type,
            query_text=query,
            query_filter=filter,
            limit=limit,
            score_threshold=score_threshold,
        )
        results = [
            {
                "id": point.id,
                "metadata": point.metadata,
                "context": point.document,
                "score": point.score,
            }
            for point in points
        ]

        return results

    def reset(self) -> None:
        self.client.delete_collection(self.type)

    def _initialize_app(self):
        if os.getenv("QDRANT_MODE") == "memory":
            self.client = QdrantClient(":memory:")
        elif os.getenv("QDRANT_MODE") == "cloud":
            self.client = QdrantClient(
                host=os.getenv("QDRANT_HOST"),
                api_key=os.getenv("QDRANT_API_KEY"),
            )
        elif os.getenv("QDRANT_MODE") == "docker":
            self.client = QdrantClient(url=os.getenv("QDRANT_URL"))
        else:
            raise ValueError("Qdrant has 3 mode: memory, cloud or docker")
        self.client._embedding_model_name = os.getenv("EMBEDDER")
        if not self.client.collection_exists(self.type):
            self.client.create_collection(
                collection_name=self.type,
                vectors_config=self.client.get_fastembed_vector_params(),
                sparse_vectors_config=self.client.get_fastembed_sparse_vector_params(),
            )

    def save(self, value: Any, metadata: Dict[str, Any]) -> None:
        self.client.add(self.type, documents=[value], metadata=[metadata or {}])
