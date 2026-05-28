# Sentinel AI

Sentinel AI is a defensive security audit platform for websites, domains, and server infrastructure. It runs authorized scans, detects exposed services, checks HTTP/TLS hardening, calculates a 0-100 risk score, writes an AI-style summary, and generates a PDF report.

> Use this tool only on systems you own or where you have explicit written permission to scan.

## Quick View

| Layer | Technology | Purpose |
| --- | --- | --- |
| Frontend | Next.js, React | Dashboard, new scan form, results, history |
| API | FastAPI | Scan creation, result API, PDF download |
| Worker | Celery | Runs scans outside the API request lifecycle |
| Scanner | Nmap, HTTPX, Python TLS audit | Open ports, services, headers, certificate checks |
| Storage | PostgreSQL | Scans, findings, reports, audit logs |
| Queue | Redis | Celery broker/result backend |
| Gateway | Nginx | Optional reverse proxy |

## Screens And Diagrams

### Demo Screenshot

![Sentinel AI dashboard preview](docs/dashboard-preview.svg)

GitHub renders the following Mermaid diagrams as visual images.


### Scan Lifecycle

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Redis
    participant Worker
    participant DB

    User->>Frontend: target + authorized=true
    Frontend->>API: POST /scan
    API->>DB: create scan(status=queued)
    API->>Redis: enqueue execute_scan(scan_id)
    API-->>Frontend: 202 Accepted + scan id
    Worker->>DB: status=running
    Worker->>Worker: nmap + HTTP headers + TLS audit
    Worker->>DB: findings + score + summary
    Worker->>DB: PDF report path
    Worker->>DB: status=completed
    Frontend->>API: GET /results/{scan_id}
    API-->>Frontend: scan result + findings
```

### Status Flow

```mermaid
stateDiagram-v2
    [*] --> queued
    queued --> running
    running --> analyzing
    analyzing --> completed
    running --> failed
    analyzing --> failed
```

## Features

- Real Nmap integration for open TCP ports, service names, and lightweight version detection.
- HTTP security header audit:
  - `Content-Security-Policy`
  - `Strict-Transport-Security`
  - `X-Frame-Options`
  - `X-Content-Type-Options`
  - `Referrer-Policy`
- TLS certificate audit for expiry and old TLS versions.
- Risk score from `0` to `100`.
- Local AI-style summary that explains the most important issues.
- PDF report generation.
- Scan history and delete endpoint.
- Docker Compose stack for full local development.
- Safety guard: `/scan` requires `authorized=true`.

## Start The Project

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Open:

| Service | URL |
| --- | --- |
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger docs | http://localhost:8000/docs |

Optional Nginx gateway:

```powershell
docker compose --profile gateway up --build
```

Gateway URL:

```text
http://localhost
```

The current summary engine is local and rule-based. The `AI_PROVIDER` setting is ready for a future Ollama or cloud model adapter.

## Environment

Main configuration is loaded from `.env`.

| Variable | Default | Description |
| --- | --- | --- |
| `DATABASE_URL` | `postgresql+psycopg://sentinel:sentinel@postgres:5432/sentinel` | PostgreSQL connection |
| `REDIS_URL` | `redis://redis:6379/0` | Celery broker/backend |
| `CORS_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000,http://localhost,http://127.0.0.1` | Allowed browser origins |
| `NMAP_PATH` | `nmap` | Nmap binary path |
| `SCAN_TIMEOUT_SECONDS` | `180` | Maximum scanner runtime per scan |
| `AI_PROVIDER` | `local` | Summary provider |

## How A Scan Works

When a user submits a scan:

1. Frontend sends `POST /scan`.
2. Backend validates `authorized=true`.
3. Target is normalized.
4. Scan is saved with `queued` status.
5. Celery worker receives `execute_scan`.
6. Worker runs Nmap:

```text
nmap -sV -O --top-ports 1000 --version-light -oX - <target>
```

7. Worker keeps only ports with `state=open`.
8. Worker checks HTTP headers and TLS.
9. Findings are saved.
10. Risk score and summary are generated.
11. PDF report is generated.

Important scanner details:

| Item | Current Behavior |
| --- | --- |
| TCP ports | Top 1000 ports |
| UDP ports | Not scanned |
| Service detection | Enabled with `-sV` |
| OS detection | Enabled with `-O` |
| Exploit scripts | Not used |
| Brute force | Not used |
| Multi-target scan | Not used |

## API Reference

### Create Scan

```http
POST /scan
Content-Type: application/json
```

```json
{
  "target": "example.com",
  "authorized": true
}
```

Response:

```json
{
  "id": "scan-uuid",
  "target": "example.com",
  "normalized_target": "example.com",
  "status": "queued",
  "score": 0,
  "summary": null,
  "error": null,
  "scanner_meta": {},
  "created_at": "2026-05-27T10:00:00Z",
  "updated_at": "2026-05-27T10:00:00Z"
}
```


Typical local development timings:

| Step | Usually Takes | Notes |
| --- | ---: | --- |
| Browser preflight `OPTIONS /scan` | `< 1s` | CORS validation |
| `POST /scan` API response | `< 1s` | Scan is queued, not completed yet |
| Nmap top 1000 TCP scan | `10-180s` | Depends on target/firewall/network |
| HTTP header audit | `1-8s` | Uses HTTPS first, then HTTP fallback |
| TLS audit | `1-8s` | Connects to port `443` |
| PDF generation | `< 2s` | Depends on findings count |

`SCAN_TIMEOUT_SECONDS=180` is the hard timeout for the scanner stage.

## Verify Nmap

Inside Docker:

```powershell
docker compose exec backend nmap --version
```

Run a direct safe check from the backend container:

```powershell
docker compose exec backend nmap -sV --top-ports 20 example.com
```

If the target is your Windows host from inside Docker, use:

```text
host.docker.internal
```

Do not use `localhost` from inside a container if you mean the Windows machine. In Docker, `localhost` means the container itself.

## Interpreting Open Ports

Example finding:

```text
53/tcp port ochiq
80/tcp port ochiq
443/tcp port ochiq
```

Meaning:

| Port | Common Service | How To Test Safely |
| ---: | --- | --- |
| `53/tcp` | DNS | `nslookup example.com <server-ip>` |
| `80/tcp` | HTTP | `curl.exe -I http://example.com` |
| `443/tcp` | HTTPS | `curl.exe -I https://example.com` |
| `22/tcp` | SSH | `Test-NetConnection example.com -Port 22` |
| `3306/tcp` | MySQL | Should usually be private only |
| `5432/tcp` | PostgreSQL | Should usually be private only |
| `6379/tcp` | Redis | Should not be public |

Windows port tests:

```powershell
Test-NetConnection example.com -Port 53
Test-NetConnection example.com -Port 80
Test-NetConnection example.com -Port 443
```

HTTP/HTTPS header tests:

```powershell
curl.exe -I http://example.com
curl.exe -I https://example.com
```

Find the IP address behind a domain:

```powershell
Resolve-DnsName example.com -Type A
nslookup example.com
```

Find your current public IP:

```powershell
curl.exe https://api.ipify.org
```

## Domain And Port Access

Browsers can open HTTP-like services:

```text
http://example.com:8080
https://example.com:8443
```

Browsers cannot directly use non-web protocols like SSH, MySQL, PostgreSQL, or Redis.

Subdomains do not map to ports by DNS alone. To use a clean domain such as:

```text
https://admin.example.com
```

you need a reverse proxy:

```mermaid
flowchart LR
    B[Browser] -->|https://admin.example.com:443| N[Nginx/Caddy/Traefik]
    N -->|proxy_pass| A[Internal admin app :8080]
```

Example Nginx reverse proxy:

```nginx
server {
    listen 443 ssl http2;
    server_name admin.example.com;

    ssl_certificate /etc/letsencrypt/live/admin.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/admin.example.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Hardening Checklist

For public web servers:

- Keep `80/tcp` open only for redirecting to HTTPS.
- Keep `443/tcp` open for the website.
- Close database/cache/admin ports from the public internet.
- Put admin panels behind VPN, IP allowlist, or strong reverse proxy authentication.
- Use strong passwords and 2FA where available.
- Keep server packages and web apps updated.
- Monitor logs for repeated failed access attempts.

For Ubuntu servers with UFW:

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 3306/tcp
sudo ufw deny 5432/tcp
sudo ufw deny 6379/tcp
sudo ufw enable
sudo ufw status
```

Find which process owns a port:

```bash
sudo ss -tulpn
```

Example Nginx security headers:

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; frame-ancestors 'self'; object-src 'none'; base-uri 'self';" always;
```

If port `53` is open and this server is not meant to be a public DNS server, close it. If it is a DNS server, make sure it is not an open resolver.

Bind example:

```conf
options {
    recursion no;
    allow-recursion { none; };
};
```

## Risk Score

Risk score is calculated from finding severity:

| Severity | Weight |
| --- | ---: |
| `Info` | `1` |
| `Low` | `6` |
| `Medium` | `14` |
| `High` | `28` |
| `Critical` | `45` |

Final score is capped at `100`.

| Score | Label |
| ---: | --- |
| `0-25` | Xavfsiz |
| `26-50` | O'rtacha xavf |
| `51-75` | Yuqori xavf |
| `76-100` | Kritik |

## Project Structure

```text
Sentinel-AI/
+-- backend/
|   +-- app/
|   |   +-- api/
|   |   +-- core/
|   |   +-- models/
|   |   +-- schemas/
|   |   +-- services/
|   |   +-- workers/
|   +-- Dockerfile
|   +-- requirements.txt
+-- frontend/
|   +-- app/
|   +-- components/
|   +-- lib/
+-- infra/
|   +-- nginx/
+-- docs/
+-- docker-compose.yml
+-- README.md
```

## Troubleshooting

### `OPTIONS /scan` returns `400 Bad Request`

The browser origin is not allowed by CORS. Add the frontend URL to `CORS_ORIGINS`:

```env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost,http://127.0.0.1
```

Recreate the backend:

```powershell
docker compose up -d --build backend worker
```

### Nmap Is Missing

Docker image installs Nmap automatically. For local non-Docker backend runs, install Nmap and make sure it is available in `PATH`.

Check:

```powershell
nmap --version
```

### Scan Stays Queued

Check worker and Redis:

```powershell
docker compose ps
docker compose logs --tail 100 worker
docker compose logs --tail 100 redis
```

### PDF Is Not Ready

The PDF is generated after scan completion. Wait until:

```text
status=completed
```

then open:

```text
http://localhost:8000/report/{scan_id}
```

## Security Boundary

Sentinel AI is designed for defensive auditing:

- It scans one target per request.
- It does not run exploit scripts.
- It does not brute-force credentials.
- It does not bypass authentication.
- It does not teach unauthorized access.

The goal is to find exposed services and weak configuration before attackers do.
