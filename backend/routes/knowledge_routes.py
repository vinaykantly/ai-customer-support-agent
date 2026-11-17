import os
import uuid
from pathlib import Path
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from backend.middleware.auth_middleware import role_required
from backend.middleware.security import is_allowed_pdf, sanitize_text
from backend.services.pdf_service import PDFService

knowledge_bp = Blueprint("knowledge", __name__, url_prefix="/api/knowledge")

@knowledge_bp.route("/upload", methods=["POST"])
@role_required(["admin"])
def upload_pdf():
    if "file" not in request.files:
        return jsonify({"error": "Bad Request", "message": "No file uploaded."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Bad Request", "message": "No file selected."}), 400

    if not is_allowed_pdf(file.filename, file.stream):
        return jsonify({"error": "Bad Request", "message": "Only valid PDF files are permitted."}), 400

    title = sanitize_text(request.form.get("title", file.filename.rsplit(".", 1)[0]))
    filename = f"{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}"
    
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / filename

    file.save(str(file_path))
    file_size = os.path.getsize(str(file_path))

    db = current_app.config["DB_MANAGER"]
    embedding_service = current_app.config["EMBEDDING_SERVICE"]

    # Create document record
    doc = db.create_knowledge_document(
        title=title,
        file_name=file.filename,
        file_path=str(file_path),
        file_size=file_size,
        uploaded_by=request.current_user["id"]
    )

    try:
        # Extract pages and chunk
        pages = PDFService.extract_text_from_pdf(file_path)
        chunks = PDFService.chunk_document(pages, doc_title=title)

        # Generate embeddings
        for c in chunks:
            c["embedding"] = embedding_service.get_embedding(c["content"])

        # Save chunks in database
        db.save_document_chunks(doc["id"], chunks)

        return jsonify({
            "message": f"Document '{title}' uploaded and indexed successfully.",
            "document": db.get_document_by_id(doc["id"]),
            "chunk_count": len(chunks)
        }), 201

    except Exception as e:
        print(f"[Knowledge] Indexing error: {e}")
        return jsonify({
            "error": "Processing Failed",
            "message": f"Failed to parse and index PDF: {str(e)}",
            "document": doc
        }), 500

@knowledge_bp.route("/documents", methods=["GET"])
def list_documents():
    db = current_app.config["DB_MANAGER"]
    docs = db.get_all_documents()
    return jsonify({"documents": docs}), 200

@knowledge_bp.route("/documents/<doc_id>/chunks", methods=["GET"])
@role_required(["admin"])
def get_chunks(doc_id):
    db = current_app.config["DB_MANAGER"]
    chunks = db.get_document_chunks(doc_id)
    return jsonify({"chunks": chunks}), 200

@knowledge_bp.route("/documents/<doc_id>/reindex", methods=["POST"])
@role_required(["admin"])
def reindex_document(doc_id):
    db = current_app.config["DB_MANAGER"]
    doc = db.get_document_by_id(doc_id)
    if not doc:
        return jsonify({"error": "Not Found", "message": "Document not found."}), 404

    file_path = doc.get("file_path")
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "Not Found", "message": "Document file no longer exists on disk."}), 404

    try:
        embedding_service = current_app.config["EMBEDDING_SERVICE"]
        pages = PDFService.extract_text_from_pdf(file_path)
        chunks = PDFService.chunk_document(pages, doc_title=doc["title"])

        for c in chunks:
            c["embedding"] = embedding_service.get_embedding(c["content"])

        db.save_document_chunks(doc["id"], chunks)

        return jsonify({
            "message": f"Document '{doc['title']}' re-indexed successfully.",
            "chunk_count": len(chunks)
        }), 200
    except Exception as e:
        return jsonify({"error": "Processing Failed", "message": str(e)}), 500

@knowledge_bp.route("/documents/<doc_id>", methods=["DELETE"])
@role_required(["admin"])
def delete_document(doc_id):
    db = current_app.config["DB_MANAGER"]
    doc = db.get_document_by_id(doc_id)
    if not doc:
        return jsonify({"error": "Not Found", "message": "Document not found."}), 404

    db.delete_document(doc_id)
    # Remove file from disk if present
    if doc.get("file_path") and os.path.exists(doc["file_path"]):
        try:
            os.remove(doc["file_path"])
        except:
            pass

    return jsonify({"message": "Document and chunks deleted successfully."}), 200

@knowledge_bp.route("/search", methods=["POST"])
def search_test():
    """Live RAG Semantic Search Test Bench"""
    data = request.get_json() or {}
    query = sanitize_text(data.get("query", ""))
    match_threshold = float(data.get("threshold", 0.25))
    match_count = int(data.get("count", 5))

    if not query:
        return jsonify({"error": "Bad Request", "message": "Query string is required."}), 400

    db = current_app.config["DB_MANAGER"]
    embedding_service = current_app.config["EMBEDDING_SERVICE"]

    query_embedding = embedding_service.get_embedding(query)
    results = db.search_similar_chunks(
        query_embedding=query_embedding,
        match_threshold=match_threshold,
        match_count=match_count
    )

    return jsonify({
        "query": query,
        "results_count": len(results),
        "results": results
    }), 200
