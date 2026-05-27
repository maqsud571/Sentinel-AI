from collections import Counter

from app.services.risk_engine import risk_label


def build_ai_summary(target: str, findings: list[dict], score: int) -> str:
    if not findings:
        return (
            f"{target} bo'yicha avtomatik tekshiruvda muhim zaiflik topilmadi. "
            "Baribir davriy patch management, monitoring va access control tekshiruvlarini davom ettirish tavsiya etiladi."
        )

    severity_counts = Counter(str(item.get("severity", "Info")) for item in findings)
    critical = severity_counts.get("Critical", 0)
    high = severity_counts.get("High", 0)
    medium = severity_counts.get("Medium", 0)
    top = sorted(findings, key=lambda item: _severity_rank(str(item.get("severity"))), reverse=True)[:3]
    top_titles = ", ".join(item["title"] for item in top)

    return (
        f"{target} uchun umumiy risk {score}/100 ({risk_label(score)}). "
        f"Topilmalar tarkibi: Critical={critical}, High={high}, Medium={medium}. "
        f"Eng muhim masalalar: {top_titles}. "
        "Avval internetga ochiq servislar va yuqori severity topilmalarni bartaraf etish, keyin header/TLS hardening va monitoringni kuchaytirish kerak."
    )


def _severity_rank(severity: str) -> int:
    return {"Info": 0, "Low": 1, "Medium": 2, "High": 3, "Critical": 4}.get(severity, 0)

