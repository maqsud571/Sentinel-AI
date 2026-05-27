# Sentinel AI Architecture

Sentinel AI monorepo quyidagi qatlamlardan iborat:

- `frontend`: Next.js dashboard, scan formasi, result viewer, history.
- `backend`: FastAPI REST API, SQLAlchemy modellari, report endpointlari.
- `worker`: Celery worker. Scan jarayoni API threadidan tashqarida bajariladi.
- `scanner`: Nmap CLI wrapper, HTTP security header analyzer, TLS auditor.
- `risk`: severity asosida 0-100 risk score hisoblaydi.
- `ai`: hozir local summarizer. Keyingi bosqichda Ollama yoki cloud API adapteri ulanadi.
- `infra`: Nginx reverse proxy.

## Xavfsizlik chegarasi

Platforma defensive audit uchun tuzilgan. API `/scan` endpointida `authorized=true` bo'lmasa scan yaratmaydi.
Nmap wrapper faqat bitta targetga xavfsiz servis aniqlash parametrlarini yuboradi:

```text
nmap -sV -O --top-ports 1000 --version-light -oX - <target>
```

Intrusive exploit scriptlar, credential brute force yoki ko'p targetli scan avtomatik qo'llanmaydi.

## Scan lifecycle

1. Foydalanuvchi target va authorization tasdig'ini yuboradi.
2. API targetni normalizatsiya qiladi, `scans` jadvaliga `queued` status bilan yozadi.
3. Celery worker scan holatini `running` qiladi.
4. Nmap, HTTP header va TLS audit bajariladi.
5. Risk score va AI summary hisoblanadi.
6. PDF report yaratiladi.
7. Scan `completed` bo'ladi yoki xatoda `failed` statusga o'tadi.

