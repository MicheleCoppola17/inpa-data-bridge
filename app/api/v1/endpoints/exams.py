from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.db.models import Exam
from app.schemas.exam import ExamPublicListResponse, ExamPublicRead

router = APIRouter(prefix="/exams", tags=["exams"])


@router.get("", response_model=ExamPublicListResponse)
async def list_exams(
    page: int = Query(0, ge=0),
    size: int = Query(20, ge=1, le=100),
    is_expired: bool | None = None,
    updated_after: datetime | None = None,
    q: str | None = None,
    sector: str | None = Query(None, alias="sector"),
    sort: str = Query("-published_at"),
    session: AsyncSession = Depends(get_session),
) -> ExamPublicListResponse:
    filters = []
    if is_expired is not None:
        filters.append(Exam.is_expired == is_expired)
    if updated_after is not None:
        filters.append(Exam.updated_at >= updated_after)
    if sector:
        filters.append(Exam.settore == sector)
    if q:
        search = f"%{q}%"
        filters.append(or_(Exam.short_title.ilike(search), Exam.descrizione.ilike(search)))

    query = select(Exam)
    count_query = select(func.count(Exam.id))

    if filters:
        query = query.where(*filters)
        count_query = count_query.where(*filters)

    sort_map = {
        "published_at": Exam.data_pubblicazione.asc(),
        "-published_at": Exam.data_pubblicazione.desc(),
        "updated_at": Exam.updated_at.asc(),
        "-updated_at": Exam.updated_at.desc(),
        "expires_at": Exam.data_scadenza.asc(),
        "-expires_at": Exam.data_scadenza.desc(),
    }
    order_by = sort_map.get(sort, Exam.data_pubblicazione.desc())

    query = query.order_by(order_by).offset(page * size).limit(size)

    exams = (await session.scalars(query)).all()
    total = await session.scalar(count_query) or 0

    return ExamPublicListResponse(
        items=[ExamPublicRead.model_validate(exam) for exam in exams],
        page=page,
        size=size,
        total=total,
    )


@router.get("/{exam_id}", response_model=ExamPublicRead)
async def get_exam(
    exam_id: str,
    session: AsyncSession = Depends(get_session),
) -> ExamPublicRead:
    exam = await session.get(Exam, exam_id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Exam not found")
    return ExamPublicRead.model_validate(exam)
