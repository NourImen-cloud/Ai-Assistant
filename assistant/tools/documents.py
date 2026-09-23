"""Document intelligence tools for reading, summarizing, and searching local files."""

import json
from pathlib import Path
from typing import Any

from assistant.tools.paths import ensure_within_home, resolve_path


def read_document(file_path: str, max_chars: int = 5000) -> dict[str, Any]:
    """Read content from PDF, Word (docx), text, markdown, or code files."""
    try:
        path = ensure_within_home(resolve_path(file_path))
        if not path.exists():
            return {"status": "error", "message": f"File not found: {path}"}
        if not path.is_file():
            return {"status": "error", "message": f"Target is a directory, not a file: {path}"}

        suffix = path.suffix.lower()
        extracted_text = ""
        meta_info = ""

        # PDF extraction
        if suffix == ".pdf":
            try:
                import pypdf

                reader = pypdf.PdfReader(str(path))
                num_pages = len(reader.pages)
                meta_info = f"PDF with {num_pages} pages."
                pages_text = []
                for idx, page in enumerate(reader.pages[:20]):  # up to 20 pages
                    t = page.extract_text() or ""
                    if t:
                        pages_text.append(f"--- Page {idx + 1} ---\n{t.strip()}")
                extracted_text = "\n\n".join(pages_text)
            except Exception as e:
                return {"status": "error", "message": f"Failed to extract PDF: {e}"}

        # DOCX extraction
        elif suffix == ".docx":
            try:
                import docx

                doc = docx.Document(str(path))
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                meta_info = f"DOCX with {len(paragraphs)} paragraphs."
                extracted_text = "\n".join(paragraphs)
            except ImportError:
                # If python-docx is not installed, read as binary/xml fallback or alert
                return {
                    "status": "error",
                    "message": "python-docx not installed. Install python-docx to read .docx files.",
                }
            except Exception as e:
                return {"status": "error", "message": f"Failed to read DOCX: {e}"}

        # Plain text, Markdown, Code, CSV, JSON
        else:
            try:
                extracted_text = path.read_text(encoding="utf-8", errors="replace")
                meta_info = f"Text document ({suffix or 'plain'})."
            except Exception as e:
                return {"status": "error", "message": f"Failed to read text file: {e}"}

        char_count = len(extracted_text)
        preview = extracted_text[:max_chars]
        truncated = char_count > max_chars

        return {
            "status": "success",
            "message": (
                f"Successfully read {path.name} ({meta_info}, {char_count} chars total"
                f"{', truncated preview' if truncated else ''}):\n\n{preview}"
            ),
            "file_name": path.name,
            "total_chars": char_count,
        }
    except Exception as exc:
        return {"status": "error", "message": f"Error reading document: {exc}"}


def summarize_document(file_path: str, focus_topic: str = "") -> dict[str, Any]:
    """Read a document and prepare an executive summary extract for the assistant."""
    read_res = read_document(file_path, max_chars=8000)
    if read_res.get("status") != "success":
        return read_res

    content = read_res.get("message", "")
    focus_hint = f"Focus particularly on '{focus_topic}'." if focus_topic else "Provide key takeaways and action items."
    return {
        "status": "success",
        "message": (
            f"Document content loaded for summary ({read_res.get('file_name')}).\n"
            f"{focus_hint}\n\n{content}"
        ),
    }


def search_documents_in_folder(
    folder_path: str = "documents", query: str = "", max_results: int = 5
) -> dict[str, Any]:
    """Search for a keyword or phrase across text and PDF files in a local folder."""
    if not query.strip():
        return {"status": "error", "message": "Search query cannot be empty."}

    try:
        folder = ensure_within_home(resolve_path(folder_path))
        if not folder.exists() or not folder.is_dir():
            return {"status": "error", "message": f"Folder not found: {folder}"}

        valid_suffixes = {".txt", ".md", ".pdf", ".py", ".json", ".csv"}
        matches = []
        lower_query = query.strip().lower()

        for item in folder.rglob("*"):
            if not item.is_file() or item.suffix.lower() not in valid_suffixes:
                continue

            try:
                text = ""
                if item.suffix.lower() == ".pdf":
                    import pypdf

                    reader = pypdf.PdfReader(str(item))
                    for idx, page in enumerate(reader.pages[:5]):
                        p_text = page.extract_text() or ""
                        if lower_query in p_text.lower():
                            matches.append({
                                "file": item.name,
                                "path": str(item),
                                "snippet": p_text[:250].replace("\n", " "),
                                "page": idx + 1,
                            })
                            break
                else:
                    text = item.read_text(encoding="utf-8", errors="ignore")
                    if lower_query in text.lower():
                        # Find snippet around query
                        start_idx = max(0, text.lower().find(lower_query) - 50)
                        snippet = text[start_idx : start_idx + 250].replace("\n", " ")
                        matches.append({
                            "file": item.name,
                            "path": str(item),
                            "snippet": f"...{snippet}...",
                        })

                if len(matches) >= max_results:
                    break
            except Exception:
                continue

        if not matches:
            return {"status": "success", "message": f"No documents in {folder} matched '{query}'."}

        formatted = [f"- {m['file']} ({m.get('path')}): {m['snippet']}" for m in matches]
        return {
            "status": "success",
            "message": f"Found {len(matches)} matching document(s) in {folder}:\n" + "\n".join(formatted),
            "matches": matches,
        }
    except Exception as exc:
        return {"status": "error", "message": f"Failed to search documents: {exc}"}
