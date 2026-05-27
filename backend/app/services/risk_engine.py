SEVERITY_WEIGHT = {
    "Info": 1,
    "Low": 6,
    "Medium": 14,
    "High": 28,
    "Critical": 45,
}


def calculate_score(findings: list[dict]) -> int:
    score = 0
    for finding in findings:
        score += SEVERITY_WEIGHT.get(str(finding.get("severity")), 1)
    return min(score, 100)


def risk_label(score: int) -> str:
    if score <= 25:
        return "Xavfsiz"
    if score <= 50:
        return "O'rtacha xavf"
    if score <= 75:
        return "Yuqori xavf"
    return "Kritik"

