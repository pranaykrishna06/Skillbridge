from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import require_role

from app.services.embedding_update_service import (
    get_embedding_sync_status,
    synchronize_all_embeddings
)


router = APIRouter(
    prefix="/api/embeddings",
    tags=["Embedding Management"]
)


# ============================================================
# 1. VIEW EMBEDDING SYNCHRONIZATION STATUS
# ============================================================

@router.get("/status")
def get_embedding_status(
    current_user: dict = Depends(require_role("Admin"))
):

    try:

        status = get_embedding_sync_status()

        return {
            "message": "Embedding status retrieved successfully.",
            "embedding_status": status
        }

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve embedding synchronization status."
        )


# ============================================================
# 2. SYNCHRONIZE ALL EMBEDDINGS
# ============================================================

@router.post("/synchronize")
def synchronize_embeddings(
    current_user: dict = Depends(require_role("Admin"))
):

    try:

        result = synchronize_all_embeddings()

        return result

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Embedding synchronization failed."
        )
