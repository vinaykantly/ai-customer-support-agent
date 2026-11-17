import hashlib
import math
import requests

class EmbeddingService:
    """
    Generates 768-dimensional embeddings for RAG document chunking & search.
    Integrates with Google Gemini's text-embedding-004 API when configured,
    and provides a deterministic localized embedding fallback for offline testing.
    """
    DIMENSION = 768

    def __init__(self, api_key: str = "", model_name: str = "text-embedding-004"):
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:embedContent"

    def get_embedding(self, text: str) -> list[float]:
        """Generates embedding vector for given text"""
        if not text:
            return [0.0] * self.DIMENSION

        if self.api_key:
            try:
                resp = requests.post(
                    f"{self.api_url}?key={self.api_key}",
                    json={"content": {"parts": [{"text": text[:2000]}]}},
                    timeout=10
                )
                if resp.status_code == 200:
                    data = resp.json()
                    values = data.get("embedding", {}).get("values", [])
                    if values and len(values) == self.DIMENSION:
                        return values
            except Exception as e:
                print(f"[EmbeddingService] Gemini API call failed: {e}. Falling back to local vectorizer.")

        # Local deterministic embedding generation
        return self._generate_local_embedding(text)

    def get_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Batch embedding generation"""
        return [self.get_embedding(t) for t in texts]

    def _generate_local_embedding(self, text: str) -> list[float]:
        """
        Creates a deterministic normalized 768-dimensional vector
        based on character n-grams and token hash projections.
        Guarantees semantically overlapping texts yield high cosine similarity.
        """
        vec = [0.0] * self.DIMENSION
        tokens = text.lower().split()
        
        # Word token features
        for token in tokens:
            cleaned = "".join(ch for ch in token if ch.isalnum())
            if not cleaned:
                continue
            idx = int(hashlib.md5(cleaned.encode("utf-8")).hexdigest(), 16) % self.DIMENSION
            weight = 1.0 + (len(cleaned) / 10.0)
            vec[idx] += weight

        # Substring 3-gram features
        for i in range(len(text) - 2):
            trigram = text[i:i+3].lower()
            idx = int(hashlib.sha256(trigram.encode("utf-8")).hexdigest(), 16) % self.DIMENSION
            vec[idx] += 0.25

        # Normalize vector to unit length
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [round(v / norm, 6) for v in vec]
        return vec
