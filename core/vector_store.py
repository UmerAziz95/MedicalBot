"""
Vector database operations using PostgreSQL + pgvector
"""

import json
import uuid
from typing import Any, Dict, List, Optional

import psycopg
from pgvector.psycopg import register_vector, Vector
from psycopg import sql
from sentence_transformers import SentenceTransformer

from config.settings import (
    EMBEDDING_MODEL_NAME,
    PGVECTOR_CONNECTION_URI,
    PGVECTOR_TABLE,
)


class VectorStore:
    """Handle vector database operations using PostgreSQL and pgvector."""

    def __init__(
        self,
        connection_uri: Optional[str] = None,
        table_name: Optional[str] = None,
        embedding_model: Optional[str] = None,
    ) -> None:
        self.connection_uri = connection_uri or PGVECTOR_CONNECTION_URI
        self.table_name = table_name or PGVECTOR_TABLE
        self.embedding_model_name = embedding_model or EMBEDDING_MODEL_NAME

        self.model = SentenceTransformer(self.embedding_model_name)
        self.embedding_dimension = len(self.model.encode("example"))

        try:
            self.conn = psycopg.connect(self.connection_uri, autocommit=True)
        except psycopg.Error as exc:  # pragma: no cover - connection guard
            raise RuntimeError(
                f"Unable to connect to PostgreSQL at {self.connection_uri}. "
                "Set PGVECTOR_CONNECTION_URI to a reachable database that has pgvector installed."
            ) from exc

        register_vector(self.conn)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Create required extensions, table, and indexes if they do not exist."""
        with self.conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute(
                sql.SQL(
                    """
                    CREATE TABLE IF NOT EXISTS {table} (
                        id TEXT PRIMARY KEY,
                        content TEXT NOT NULL,
                        metadata JSONB,
                        embedding vector({dimension}) NOT NULL
                    );
                    """
                ).format(
                    table=sql.Identifier(self.table_name),
                    dimension=sql.Literal(self.embedding_dimension),
                )
            )
            cur.execute(
                sql.SQL(
                    """
                    CREATE INDEX IF NOT EXISTS {index_name}
                    ON {table}
                    USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = 100);
                    """
                ).format(
                    index_name=sql.Identifier(f"{self.table_name}_embedding_idx"),
                    table=sql.Identifier(self.table_name),
                )
            )

    def _embed(self, text: str) -> Vector:
        """Create an embedding vector for the provided text."""
        embedding = self.model.encode(text, normalize_embeddings=True)
        return Vector(embedding.tolist())

    def store_chunks(
        self,
        chunks: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """Store text chunks in the vector database."""
        if metadatas is None:
            metadatas = [{} for _ in chunks]
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in chunks]

        stored_ids: List[str] = []
        print(f"Storing {len(chunks)} chunks in PostgreSQL vector store...")
        with self.conn.cursor() as cur:
            for idx, chunk in enumerate(chunks):
                chunk_id = ids[idx] if idx < len(ids) else str(uuid.uuid4())
                metadata = metadatas[idx] if idx < len(metadatas) else {}
                embedding = self._embed(chunk)
                cur.execute(
                    sql.SQL(
                        """
                        INSERT INTO {table} (id, content, metadata, embedding)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id)
                        DO UPDATE SET content = EXCLUDED.content,
                                      metadata = EXCLUDED.metadata,
                                      embedding = EXCLUDED.embedding;
                        """
                    ).format(table=sql.Identifier(self.table_name)),
                    (chunk_id, chunk, json.dumps(metadata), embedding),
                )
                stored_ids.append(chunk_id)
        print("✅ All chunks stored successfully!")
        return stored_ids

    def query_similar_chunks(self, question: str, n_results: int = 3) -> List[str]:
        """Query the vector database for similar chunks."""
        results = self.search(question, k=n_results)
        return [res["content"] for res in results]

    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        embedding = self._embed(query)
        with self.conn.cursor() as cur:
            cur.execute(
                sql.SQL(
                    """
                    SELECT id, content, metadata,
                           1 - (embedding <=> %s) AS similarity
                    FROM {table}
                    ORDER BY embedding <=> %s
                    LIMIT %s;
                    """
                ).format(table=sql.Identifier(self.table_name)),
                (embedding, embedding, k),
            )
            rows = cur.fetchall()

        formatted_results: List[Dict[str, Any]] = []
        for row in rows:
            doc_id, content, metadata, similarity = row
            formatted_results.append(
                {
                    "id": doc_id,
                    "content": content,
                    "metadata": metadata or {},
                    "similarity": similarity,
                }
            )
        print(f"Found {len(formatted_results)} matching documents")
        return formatted_results

    def add_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a single text chunk with metadata."""
        doc_id = str(uuid.uuid4())
        self.store_chunks([text], metadatas=[metadata or {}], ids=[doc_id])
        return doc_id

    def clear(self) -> None:
        """Clear all data from the collection."""
        self.clear_collection()

    def clear_collection(self) -> None:
        """Clear all data from the collection."""
        with self.conn.cursor() as cur:
            cur.execute(sql.SQL("TRUNCATE TABLE {table};").format(table=sql.Identifier(self.table_name)))
        print("✅ Collection cleared successfully!")

    def count(self) -> int:
        """Get the number of documents in the collection."""
        with self.conn.cursor() as cur:
            cur.execute(sql.SQL("SELECT COUNT(*) FROM {table};").format(table=sql.Identifier(self.table_name)))
            row = cur.fetchone()
            return row[0] if row else 0

    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the current collection."""
        try:
            return {
                "name": self.table_name,
                "document_count": self.count(),
            }
        except Exception as exc:  # pragma: no cover - defensive logging
            return {"error": str(exc)}

    def distinct_sources(self, limit: int = 200) -> List[str]:
        """Return distinct source values recorded in metadata."""
        with self.conn.cursor() as cur:
            cur.execute(
                sql.SQL(
                    """
                    SELECT DISTINCT metadata ->> 'source'
                    FROM {table}
                    WHERE metadata ? 'source'
                    LIMIT %s;
                    """
                ).format(table=sql.Identifier(self.table_name)),
                (limit,),
            )
            return [row[0] for row in cur.fetchall() if row[0]]

    def __del__(self) -> None:
        try:
            if hasattr(self, "conn"):
                self.conn.close()
        except Exception:
            pass
