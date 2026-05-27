import socket
import ssl
from datetime import datetime, timezone


def audit_tls(target: str) -> list[dict]:
    findings: list[dict] = []
    context = ssl.create_default_context()
    try:
        with socket.create_connection((target, 443), timeout=8) as sock:
            with context.wrap_socket(sock, server_hostname=target) as tls:
                cert = tls.getpeercert()
                version = tls.version()
    except Exception as exc:
        return [
            {
                "title": "TLS audit bajarilmadi",
                "severity": "Info",
                "category": "tls",
                "evidence": str(exc),
                "recommendation": "Agar HTTPS ishlashi kerak bo'lsa, 443-port va sertifikat konfiguratsiyasini tekshiring.",
                "details": {},
            }
        ]

    not_after = cert.get("notAfter")
    if not_after:
        expires_at = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        days_left = (expires_at - datetime.now(timezone.utc)).days
        if days_left < 14:
            findings.append(
                {
                    "title": "TLS sertifikat muddati tugashga yaqin",
                    "severity": "High" if days_left < 0 else "Medium",
                    "category": "tls",
                    "evidence": f"Sertifikat {days_left} kun ichida tugaydi.",
                    "recommendation": "Sertifikatni yangilang va avtomatik renew jarayonini tekshiring.",
                    "details": {"expires_at": expires_at.isoformat()},
                }
            )

    if version in {"TLSv1", "TLSv1.1"}:
        findings.append(
            {
                "title": "Eski TLS versiyasi ishlatilmoqda",
                "severity": "High",
                "category": "tls",
                "evidence": f"Kelishilgan versiya: {version}",
                "recommendation": "TLS 1.2 yoki TLS 1.3 ni majburiy qiling.",
                "details": {"tls_version": version},
            }
        )

    return findings

