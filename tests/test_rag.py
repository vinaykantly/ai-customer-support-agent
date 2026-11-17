import pytest
from pathlib import Path
from backend.services.pdf_service import PDFService
from backend.services.embedding_service import EmbeddingService

def test_pdf_extraction_and_chunking():
    pdf_path = Path("uploads/support_policy_v2.pdf")
    assert pdf_path.exists()

    pages = PDFService.extract_text_from_pdf(pdf_path)
    assert len(pages) > 0
    assert "Official Company Support Policy" in pages[0]["text"]

    chunks = PDFService.chunk_document(pages, doc_title="Support Policy")
    assert len(chunks) > 0
    assert chunks[0]["metadata"]["doc_title"] == "Support Policy"

def test_embedding_service_dimension_and_consistency():
    service = EmbeddingService()
    emb1 = service.get_embedding("Refund and billing dispute guidelines")
    emb2 = service.get_embedding("Refund and billing dispute standards")
    emb3 = service.get_embedding("Completely unrelated text about astronomy and stars")

    assert len(emb1) == 768
    assert len(emb2) == 768

    # Cosine similarity between emb1 and emb2 should be high
    from backend.database.db_manager import DatabaseManager
    sim_close = DatabaseManager._cosine_similarity(emb1, emb2)
    sim_far = DatabaseManager._cosine_similarity(emb1, emb3)

    assert sim_close > sim_far

def test_rag_semantic_search_endpoint(client):
    res = client.post("/api/knowledge/search", json={
        "query": "refund policy and money back guarantee",
        "count": 2
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["results_count"] > 0
    assert "Official Company Support Policy" in data["results"][0]["doc_title"]
