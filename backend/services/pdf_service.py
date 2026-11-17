import io
from pathlib import Path
from pypdf import PdfReader

class PDFService:
    """
    Extracts text from PDF documents and performs semantic text chunking
    with sliding window overlap and structural metadata.
    """
    CHUNK_SIZE = 600
    CHUNK_OVERLAP = 100

    @classmethod
    def extract_text_from_pdf(cls, file_path_or_bytes) -> list[dict]:
        """
        Extracts text page-by-page.
        Returns a list of dicts: [{"page": 1, "text": "..."}]
        """
        pages_content = []
        try:
            if isinstance(file_path_or_bytes, (str, Path)):
                reader = PdfReader(str(file_path_or_bytes))
            else:
                reader = PdfReader(io.BytesIO(file_path_or_bytes))

            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                # Normalize spaces and newlines
                clean_text = " ".join(text.split())
                if clean_text:
                    pages_content.append({
                        "page": page_idx + 1,
                        "text": clean_text
                    })
        except Exception as e:
            print(f"[PDFService] Error extracting PDF text: {e}")
            raise e

        return pages_content

    @classmethod
    def chunk_document(cls, pages_content: list[dict], doc_title: str) -> list[dict]:
        """
        Divides page texts into overlapping chunks with metadata.
        Returns list of chunks:
        [{
            "chunk_index": 1,
            "content": "...",
            "metadata": {"page": 1, "doc_title": "..."}
        }]
        """
        chunks = []
        global_index = 1

        for p in pages_content:
            page_num = p["page"]
            text = p["text"]
            
            if len(text) <= cls.CHUNK_SIZE:
                chunks.append({
                    "chunk_index": global_index,
                    "content": text,
                    "metadata": {
                        "page": page_num,
                        "doc_title": doc_title,
                        "char_count": len(text)
                    }
                })
                global_index += 1
                continue

            # Sliding window chunking
            start = 0
            while start < len(text):
                end = min(start + cls.CHUNK_SIZE, len(text))
                
                # If not at the very end, try breaking at sentence or space boundary
                if end < len(text):
                    last_period = text.rfind(".", start, end)
                    if last_period != -1 and last_period > start + (cls.CHUNK_SIZE // 2):
                        end = last_period + 1
                    else:
                        last_space = text.rfind(" ", start, end)
                        if last_space != -1 and last_space > start + (cls.CHUNK_SIZE // 2):
                            end = last_space + 1

                chunk_text = text[start:end].strip()
                if chunk_text:
                    chunks.append({
                        "chunk_index": global_index,
                        "content": chunk_text,
                        "metadata": {
                            "page": page_num,
                            "doc_title": doc_title,
                            "char_count": len(chunk_text)
                        }
                    })
                    global_index += 1

                if end >= len(text):
                    break
                start = end - cls.CHUNK_OVERLAP

        return chunks
