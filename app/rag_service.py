import json
import pickle
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from flask import current_app
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .extensions import db
from .models import ChatLog, NoteChunk

try:
    import faiss
except Exception:  # pragma: no cover - optional dependency varies by platform.
    faiss = None

try:
    from google import genai
except Exception:  # pragma: no cover - app still works without Gemini installed.
    genai = None


@dataclass
class RetrievedChunk:
    chunk: NoteChunk
    score: float


class RAGService:
    def __init__(self, user_id):
        self.user_id = user_id
        self.vector_dir = Path(current_app.instance_path, current_app.config["VECTOR_FOLDER"])
        self.vector_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.vector_dir / f"user_{user_id}_faiss.index"
        self.meta_path = self.vector_dir / f"user_{user_id}_meta.json"
        self.tfidf_path = self.vector_dir / f"user_{user_id}_tfidf.pkl"

    def rebuild_index(self):
        chunks = (
            NoteChunk.query.filter_by(user_id=self.user_id)
            .order_by(NoteChunk.id.asc())
            .all()
        )
        texts = [chunk.content for chunk in chunks]
        metadata = [{"chunk_id": chunk.id} for chunk in chunks]
        self.meta_path.write_text(json.dumps(metadata), encoding="utf-8")

        if not texts:
            self._remove_index_files()
            return

        vectors = self._embed_texts(texts)
        if vectors is not None and faiss is not None:
            vectors = vectors.astype("float32")
            faiss.normalize_L2(vectors)
            index = faiss.IndexFlatIP(vectors.shape[1])
            index.add(vectors)
            faiss.write_index(index, str(self.index_path))

        vectorizer = TfidfVectorizer(stop_words="english", max_features=8000)
        matrix = vectorizer.fit_transform(texts)
        with self.tfidf_path.open("wb") as file:
            pickle.dump({"vectorizer": vectorizer, "matrix": matrix, "chunk_ids": [c.id for c in chunks]}, file)

    def retrieve(self, question, top_k=5):
        results = self._retrieve_with_faiss(question, top_k)
        if results:
            return results
        return self._retrieve_with_tfidf(question, top_k)

    def answer(self, question):
        retrieved = self.retrieve(question)
        if not retrieved:
            answer = "I could not find relevant content. Upload notes first, then ask a question about them."
            log = ChatLog(user_id=self.user_id, question=question, answer=answer, sources="[]")
            db.session.add(log)
            db.session.commit()
            return answer, [], log.id

        context_blocks = []
        sources = []
        for item in retrieved:
            note = item.chunk.note
            context_blocks.append(
                f"Source: {note.filename}, page {item.chunk.page_number}\n{item.chunk.content}"
            )
            sources.append(
                {
                    "note": note.filename,
                    "page": item.chunk.page_number,
                    "score": round(float(item.score), 4),
                }
            )

        prompt = self._build_prompt(question, "\n\n---\n\n".join(context_blocks))
        answer = self._generate_answer(prompt) or self._fallback_answer(question, retrieved)

        log = ChatLog(
            user_id=self.user_id,
            question=question,
            answer=answer,
            sources=json.dumps(sources),
        )
        db.session.add(log)
        db.session.commit()
        return answer, sources, log.id

    def _retrieve_with_faiss(self, question, top_k):
        if faiss is None or not self.index_path.exists() or not self.meta_path.exists():
            return []

        query_vector = self._embed_texts([question], task_type="retrieval_query")
        if query_vector is None:
            return []

        index = faiss.read_index(str(self.index_path))
        query_vector = query_vector.astype("float32")
        faiss.normalize_L2(query_vector)
        scores, positions = index.search(query_vector, top_k)
        metadata = json.loads(self.meta_path.read_text(encoding="utf-8"))
        chunk_ids = []
        score_by_id = {}
        for position, score in zip(positions[0], scores[0]):
            if position < 0 or position >= len(metadata):
                continue
            chunk_id = metadata[position]["chunk_id"]
            chunk_ids.append(chunk_id)
            score_by_id[chunk_id] = float(score)

        chunks = NoteChunk.query.filter(NoteChunk.id.in_(chunk_ids)).all()
        chunk_by_id = {chunk.id: chunk for chunk in chunks}
        return [
            RetrievedChunk(chunk_by_id[chunk_id], score_by_id[chunk_id])
            for chunk_id in chunk_ids
            if chunk_id in chunk_by_id
        ]

    def _retrieve_with_tfidf(self, question, top_k):
        if not self.tfidf_path.exists():
            return []
        with self.tfidf_path.open("rb") as file:
            data = pickle.load(file)
        query_matrix = data["vectorizer"].transform([question])
        scores = cosine_similarity(query_matrix, data["matrix"]).flatten()
        if scores.size == 0:
            return []
        ranked = np.argsort(scores)[::-1][:top_k]
        chunk_ids = [data["chunk_ids"][idx] for idx in ranked if scores[idx] > 0]
        score_by_id = {data["chunk_ids"][idx]: float(scores[idx]) for idx in ranked}
        chunks = NoteChunk.query.filter(NoteChunk.id.in_(chunk_ids)).all()
        chunk_by_id = {chunk.id: chunk for chunk in chunks}
        return [
            RetrievedChunk(chunk_by_id[chunk_id], score_by_id[chunk_id])
            for chunk_id in chunk_ids
            if chunk_id in chunk_by_id
        ]

    def _embed_texts(self, texts, task_type="retrieval_document"):
        api_key = current_app.config.get("GEMINI_API_KEY")
        if not api_key or genai is None:
            return None
        client = genai.Client(api_key=api_key)
        model = current_app.config["GEMINI_EMBEDDING_MODEL"]
        vectors = []
        try:
            for text in texts:
                result = _embed_content(client, model, text, task_type)
                vectors.append(result)
        except Exception:
            return None
        return np.array(vectors, dtype=np.float32)

    def _generate_answer(self, prompt):
        api_key = current_app.config.get("GEMINI_API_KEY")
        if not api_key or genai is None:
            return None
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=current_app.config["GEMINI_MODEL"],
                contents=prompt,
            )
            return getattr(response, "text", None)
        except Exception:
            return None

    def _fallback_answer(self, question, retrieved):
        best = retrieved[0].chunk
        if current_app.config.get("GEMINI_API_KEY"):
            prefix = (
                "Gemini is configured, but the generation request failed. "
                "Check that GEMINI_API_KEY, GEMINI_MODEL, quota, and API access are valid. "
                "The local retriever still found this relevant excerpt from your notes:\n\n"
            )
        else:
            prefix = (
                "Gemini answer generation is disabled because GEMINI_API_KEY is not configured. "
                "The local retriever still found this relevant excerpt from your notes:\n\n"
            )
        return (
            f"{prefix}{best.content[:1200]}"
        )

    def _build_prompt(self, question, context):
        return (
            "You are a college notes RAG assistant. Answer only from the provided context. "
            "If the answer is not present, say that the notes do not contain enough information. "
            "Cite source filenames and page numbers when useful.\n\n"
            f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
        )

    def _remove_index_files(self):
        for path in (self.index_path, self.meta_path, self.tfidf_path):
            if path.exists():
                path.unlink()


def _embed_content(client, model, text, task_type):
    normalized_task = task_type.upper()
    try:
        response = client.models.embed_content(
            model=model,
            contents=text,
            config={"task_type": normalized_task},
        )
    except TypeError:
        response = client.models.embed_content(model=model, contents=text)

    if hasattr(response, "embeddings") and response.embeddings:
        embedding = response.embeddings[0]
        values = getattr(embedding, "values", None)
        if values is not None:
            return values
        if isinstance(embedding, dict):
            return embedding.get("values") or embedding.get("embedding")

    if hasattr(response, "embedding"):
        embedding = response.embedding
        values = getattr(embedding, "values", None)
        if values is not None:
            return values
        if isinstance(embedding, dict):
            return embedding.get("values") or embedding.get("embedding")

    if isinstance(response, dict):
        embeddings = response.get("embeddings")
        if embeddings:
            first = embeddings[0]
            if isinstance(first, dict):
                return first.get("values") or first.get("embedding")
        return response.get("embedding")

    raise ValueError("Gemini embedding response did not include vector values.")
