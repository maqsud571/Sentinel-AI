from sqlalchemy.orm import selectinload

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.scan import Finding, Report, Scan, ScanStatus, Severity
from app.services.ai_analyzer import build_ai_summary
from app.services.http_security import analyze_http_headers
from app.services.nmap_scanner import run_nmap_scan
from app.services.report_generator import generate_pdf_report
from app.services.risk_engine import calculate_score
from app.services.tls_audit import audit_tls
from app.services.vulnerability_scanner import analyze_service_exposure


@celery_app.task(name="execute_scan")
def execute_scan(scan_id: str) -> None:
    db = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if scan is None:
            return

        scan.status = ScanStatus.running
        db.commit()

        findings: list[dict] = []
        nmap_result = run_nmap_scan(scan.normalized_target)
        scan.scanner_meta = {"nmap": nmap_result.raw_meta, "os_guess": nmap_result.os_guess}
        findings.extend(_findings_from_ports(nmap_result.ports))
        findings.extend(analyze_service_exposure(nmap_result.ports))
        findings.extend(analyze_http_headers(scan.normalized_target))
        findings.extend(audit_tls(scan.normalized_target))

        scan.status = ScanStatus.analyzing
        db.commit()

        for item in findings:
            db.add(
                Finding(
                    scan_id=scan.id,
                    title=item["title"],
                    severity=Severity(item["severity"]),
                    category=item["category"],
                    evidence=item.get("evidence"),
                    recommendation=item.get("recommendation"),
                    details=item.get("details", {}),
                )
            )

        score = calculate_score(findings)
        scan.score = score
        scan.summary = build_ai_summary(scan.normalized_target, findings, score)
        scan.status = ScanStatus.completed
        db.commit()

        scan = db.query(Scan).options(selectinload(Scan.findings)).filter(Scan.id == scan_id).one()
        report_path = generate_pdf_report(scan)
        db.add(Report(scan_id=scan.id, pdf_path=report_path))
        db.commit()
    except Exception as exc:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if scan is not None:
            scan.status = ScanStatus.failed
            scan.error = str(exc)
            db.commit()
    finally:
        db.close()


def _findings_from_ports(ports) -> list[dict]:
    findings: list[dict] = []
    risky_ports = {
        21: ("FTP ochiq", "FTP o'rniga SFTP/SSH ishlating yoki internetdan cheklang.", "Medium"),
        22: ("SSH ochiq", "SSH uchun MFA, kalit asosidagi auth va allowlist qo'llang.", "Info"),
        23: ("Telnet ochiq", "Telnetni o'chiring va SSH ga o'ting.", "Critical"),
        3306: ("MySQL internetga ochiq", "DB portini private networkga cheklang.", "High"),
        5432: ("PostgreSQL internetga ochiq", "DB portini private networkga cheklang.", "High"),
        6379: ("Redis internetga ochiq", "Redis bind/ACL/password sozlamalarini tekshiring va portni yopiq tarmoqqa oling.", "Critical"),
        9200: ("Elasticsearch internetga ochiq", "Auth va network policy bilan cheklang.", "Critical"),
    }
    for port in ports:
        title, recommendation, severity = risky_ports.get(
            port.port,
            (f"{port.port}/{port.protocol} port ochiq", "Servis zarurligi, versiyasi va access control sozlamalarini tekshiring.", "Info"),
        )
        evidence = " ".join(part for part in [port.service, port.product, port.version] if part)
        findings.append(
            {
                "title": title,
                "severity": severity,
                "category": "open_port",
                "evidence": evidence or f"{port.port}/{port.protocol} open",
                "recommendation": recommendation,
                "details": {
                    "port": port.port,
                    "protocol": port.protocol,
                    "service": port.service,
                    "product": port.product,
                    "version": port.version,
                },
            }
        )
    return findings
