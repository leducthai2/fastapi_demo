from qdrant_client import QdrantClient, models
from qdrant_client.http.models import VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer

from uuid import uuid4


class ProjectCollectionHelper:
    def __init__(self, qdrant_host: str, qdrant_port: int):
        self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.collection_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.collection_name = f"project_for_testing_n8n"
        self.project_names_dir = 'projects/asset/projects.txt'
        self.vector_size = 384

    async def upload_points(self, data):
        if self.client.collection_exists(self.collection_name):
            self.client.delete_collection(self.collection_name)

        # create new collection
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size = self.vector_size,
                distance=Distance.COSINE,
            ),
        )

        points = []

        for record in data:
            p_id = record["project_id"]
            p_name = record["project_name"]
            point = PointStruct(
                id=str(uuid4()),
                vector=self.collection_model.encode(str(p_id)).tolist(),
                payload={"name": p_name},
            )
            points.append(point)
                    
        print(len(points))

        try:
            self.client.upload_points(
                collection_name=self.collection_name,
                points=points,
                wait=True
            )
            count = self.client.count(collection_name=self.collection_name)
            print(f"Upload successful. Collection has {count.count} points")
        except Exception as e:
            print(f"Upload failed: {e}")
