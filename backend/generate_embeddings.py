"""
Placeholder module for embedding generation.
Prevents missing-import errors in editors and returns a clear message if invoked.

If you want this to actually (re)generate embeddings, replace the stub in
`generate_all_embeddings` with your real implementation.
"""

from typing import Dict, Any


def generate_all_embeddings() -> Dict[str, Any]:
    return {
        "status": "not_implemented",
        "message": (
            "Embedding generation is not enabled in this build. Existing embeddings are used. "
            "Provide a real implementation in backend/generate_embeddings.py if needed."
        ),
    }



