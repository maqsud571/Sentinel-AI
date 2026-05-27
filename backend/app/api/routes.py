from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.core.database import get_db
from app.models.audit_log import AuditLog
from app.models.scan import Finding, Report, Scan
from app.schemas.scan import HistoryItem, ScanCreate, ScanOut, ScanResult
from app.services.target import normalize_target
from app.workers.tasks import execute_scan

router = APIRouter()


@router.post("/scan", response_model=ScanOut, status_code=202)
def create_scan(payload: ScanCreate, db: Session = Depends(get_db)) -> Scan:
    if not payload.authorized:
        raise HTTPException(status_code=400, detail="Scan qilish uchun target sizga tegishli yoki ruxsat borligini tasdiqlang.")
    try:
        normalized = normalize_target(payload.target)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    scan = Scan(target=payload.target.strip(), normalized_target=normalized)
    db.add(scan)
    db.commit()
    db.refresh(scan)
    db.add(AuditLog(action="scan.created", entity_id=scan.id, event_meta={"target": normalized}))
    db.commit()
    execute_scan.delay(scan.id)
    return scan


@router.get("/scan/{scan_id}", response_model=ScanOut)
def get_scan(scan_id: str, db: Session = Depends(get_db)) -> Scan:
    scan = db.get(Scan, scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan topilmadi.")
    return scan


@router.get("/results/{scan_id}", response_model=ScanResult)
def get_results(scan_id: str, db: Session = Depends(get_db)) -> Scan:
    scan = db.scalars(select(Scan).options(selectinload(Scan.findings)).where(Scan.id == scan_id)).first()
    if scan is None:
        raise HTTPException(status_code=404, detail="Natija topilmadi.")
    return scan


@router.get("/report/{scan_id}")
def download_report(scan_id: str, db: Session = Depends(get_db)) -> FileResponse:
    report = db.scalars(select(Report).where(Report.scan_id == scan_id)).first()
    if report is None:
        raise HTTPException(status_code=404, detail="Report hali yaratilmagan.")
    return FileResponse(report.pdf_path, media_type="application/pdf", filename=f"sentinel-report-{scan_id}.pdf")


@router.get("/history", response_model=list[HistoryItem])
def history(db: Session = Depends(get_db)) -> list[HistoryItem]:
    rows = db.execute(
        select(Scan, func.count(Finding.id).label("findings_count"))
        .outerjoin(Finding)
        .group_by(Scan.id)
        .order_by(desc(Scan.created_at))
        .limit(settings.max_history_rows)
    ).all()
    return [
        HistoryItem(
            id=scan.id,
            target=scan.target,
            status=scan.status.value,
            score=scan.score,
            findings_count=count,
            created_at=scan.created_at,
        )
        for scan, count in rows
    ]


@router.delete("/scan/{scan_id}", status_code=204)
def delete_scan(scan_id: str, db: Session = Depends(get_db)) -> None:
    scan = db.get(Scan, scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan topilmadi.")
    db.add(AuditLog(action="scan.deleted", entity_id=scan.id, event_meta={"target": scan.normalized_target}))
    db.delete(scan)
    db.commit()
