from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.dependencies import require_role

from app.services.notification_service import (
    get_user_notifications,
    get_unread_notification_count,
    mark_notification_as_read,
    mark_all_notifications_as_read,
    delete_notification
)


router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"]
)


# ============================================================
# COMMON AUTHENTICATION
# ============================================================

def get_authenticated_user_id(current_user: dict):

    return current_user["user_id"]


# ============================================================
# 1. GET ALL NOTIFICATIONS
# ============================================================

@router.get("/")
def get_notifications(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: dict = Depends(
        require_role("Student", "Recruiter")
    )
):

    user_id = get_authenticated_user_id(current_user)

    try:

        notifications = get_user_notifications(
            user_id=user_id,
            limit=limit,
            offset=offset
        )

        return {
            "message": "Notifications retrieved successfully.",
            "user_id": user_id,
            "role": current_user["role"],
            "total_notifications": len(notifications),
            "notifications": notifications
        }

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve notifications."
        )


# ============================================================
# 2. GET UNREAD NOTIFICATION COUNT
# ============================================================

@router.get("/unread-count")
def get_unread_count(
    current_user: dict = Depends(
        require_role("Student", "Recruiter")
    )
):

    user_id = get_authenticated_user_id(current_user)

    try:

        count = get_unread_notification_count(user_id)

        return {
            "user_id": user_id,
            "unread_count": count
        }

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve unread notification count."
        )


# ============================================================
# 3. MARK A NOTIFICATION AS READ
# ============================================================

@router.patch("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    current_user: dict = Depends(
        require_role("Student", "Recruiter")
    )
):

    user_id = get_authenticated_user_id(current_user)

    try:

        updated = mark_notification_as_read(
            user_id=user_id,
            notification_id=notification_id
        )

        if not updated:

            raise HTTPException(
                status_code=404,
                detail="Notification not found."
            )

        return {
            "message": "Notification marked as read.",
            "notification_id": notification_id
        }

    except HTTPException:
        raise

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Unable to update notification."
        )


# ============================================================
# 4. MARK ALL NOTIFICATIONS AS READ
# ============================================================

@router.patch("/read-all")
def mark_all_as_read(
    current_user: dict = Depends(
        require_role("Student", "Recruiter")
    )
):

    user_id = get_authenticated_user_id(current_user)

    try:

        updated_count = mark_all_notifications_as_read(user_id)

        return {
            "message": "All notifications marked as read.",
            "updated_notifications": updated_count
        }

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Unable to update notifications."
        )


# ============================================================
# 5. DELETE A NOTIFICATION
# ============================================================

@router.delete("/{notification_id}")
def remove_notification(
    notification_id: int,
    current_user: dict = Depends(
        require_role("Student", "Recruiter")
    )
):

    user_id = get_authenticated_user_id(current_user)

    try:

        deleted = delete_notification(
            user_id=user_id,
            notification_id=notification_id
        )

        if not deleted:

            raise HTTPException(
                status_code=404,
                detail="Notification not found."
            )

        return {
            "message": "Notification deleted successfully.",
            "notification_id": notification_id
        }

    except HTTPException:
        raise

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Unable to delete notification."
        )