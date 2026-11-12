from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import require_role
from app.services.graph_sync_service import synchronize_graph
from app.services.graph_index_service import create_graph_indexes

router = APIRouter(
    prefix="/api/graph",
    tags=["Graph Synchronization"]
)


@router.post("/sync")
def sync_graph(
    current_user: dict = Depends(require_role("Admin"))
):
    try:
        result = synchronize_graph()
        return result

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Graph synchronization failed: {str(error)}"
        )

@router.post("/create-indexes")
def create_indexes(
    current_user: dict = Depends(require_role("Admin"))
):

    try:

        result = create_graph_indexes()

        return result

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Graph index creation failed: {str(error)}"
        )
