import httpx

from app.services.target import http_url_for_target

SECURITY_HEADERS = {
    "content-security-policy": ("CSP yo'q", "Content-Security-Policy headerini qo'shing.", "Medium"),
    "strict-transport-security": ("HSTS yo'q", "Strict-Transport-Security headerini yoqing.", "Medium"),
    "x-frame-options": ("X-Frame-Options yo'q", "Clickjackingdan himoya uchun X-Frame-Options yoki CSP frame-ancestors sozlang.", "Low"),
    "x-content-type-options": ("X-Content-Type-Options yo'q", "nosniff qiymatini qo'shing.", "Low"),
    "referrer-policy": ("Referrer-Policy yo'q", "Referrer-Policy headerini aniq belgilang.", "Low"),
}


def analyze_http_headers(target: str) -> list[dict]:
    findings: list[dict] = []
    for prefer_https in (True, False):
        try:
            response = httpx.get(http_url_for_target(target, prefer_https), timeout=8, follow_redirects=True)
            headers = {key.lower(): value for key, value in response.headers.items()}
            break
        except httpx.HTTPError:
            headers = {}
    else:
        return [
            {
                "title": "HTTP servisga ulanish imkoni bo'lmadi",
                "severity": "Info",
                "category": "http",
                "evidence": "HTTP/HTTPS so'rov javob bermadi.",
                "recommendation": "Agar web servis bo'lishi kerak bo'lsa, firewall va servis holatini tekshiring.",
                "details": {},
            }
        ]

    for header, (title, recommendation, severity) in SECURITY_HEADERS.items():
        if header not in headers:
            findings.append(
                {
                    "title": title,
                    "severity": severity,
                    "category": "http_headers",
                    "evidence": f"{header} headeri topilmadi.",
                    "recommendation": recommendation,
                    "details": {"header": header},
                }
            )

    return findings

