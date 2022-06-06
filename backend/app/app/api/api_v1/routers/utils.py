from typing import Any

from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import models, schemas
from app import dependencies as deps
from app.core.celery_app import celery_app
from app.dependencies import get_db
from app.utils import send_test_email

router = APIRouter()


@router.post("/test-celery/", response_model=schemas.Msg, status_code=201)
def test_celery(
    msg: schemas.Msg,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Test Celery worker.
    """
    celery_app.send_task("app.worker.test_celery", args=[msg.msg])
    return {"msg": "Word received"}


@router.post("/test-email/", response_model=schemas.Msg, status_code=201)
def test_email(
    email_to: EmailStr,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Test emails.
    """
    send_test_email(email_to=email_to)
    return {"msg": "Test email sent"}


def health_check(db: Session = Depends(get_db)):
    try:
        db.execute('select 1')
    except Exception:
        return "Failing"
    else:
        return "OK"
