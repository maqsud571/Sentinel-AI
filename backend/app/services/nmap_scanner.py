import shutil
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass

from app.core.config import settings


@dataclass
class PortService:
    port: int
    protocol: str
    state: str
    service: str | None
    product: str | None
    version: str | None


@dataclass
class NmapResult:
    ports: list[PortService]
    os_guess: str | None
    raw_meta: dict


SAFE_ARGS = [
    "-sV",
    "-O",
    "--top-ports",
    "1000",
    "--version-light",
    "-oX",
    "-",
]


def run_nmap_scan(target: str) -> NmapResult:
    nmap_path = settings.nmap_path
    if not shutil.which(nmap_path):
        raise RuntimeError("nmap topilmadi. Docker orqali ishga tushiring yoki lokal PATH ga nmap o'rnating.")

    command = [nmap_path, *SAFE_ARGS, target]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=settings.scan_timeout_seconds,
        check=False,
    )
    if completed.returncode not in (0, 1):
        raise RuntimeError(completed.stderr.strip() or "nmap scan bajarilmadi.")

    return parse_nmap_xml(completed.stdout, command)


def parse_nmap_xml(xml_text: str, command: list[str]) -> NmapResult:
    root = ET.fromstring(xml_text)
    host = root.find("host")
    if host is None:
        return NmapResult(ports=[], os_guess=None, raw_meta={"command": scrub_command(command)})

    ports: list[PortService] = []
    for port_el in host.findall("./ports/port"):
        state_el = port_el.find("state")
        state = state_el.attrib.get("state", "unknown") if state_el is not None else "unknown"
        if state != "open":
            continue

        service_el = port_el.find("service")
        ports.append(
            PortService(
                port=int(port_el.attrib["portid"]),
                protocol=port_el.attrib.get("protocol", "tcp"),
                state=state,
                service=service_el.attrib.get("name") if service_el is not None else None,
                product=service_el.attrib.get("product") if service_el is not None else None,
                version=service_el.attrib.get("version") if service_el is not None else None,
            )
        )

    os_guess = None
    os_match = host.find("./os/osmatch")
    if os_match is not None:
        os_guess = os_match.attrib.get("name")

    return NmapResult(ports=ports, os_guess=os_guess, raw_meta={"command": scrub_command(command)})


def scrub_command(command: list[str]) -> list[str]:
    return ["nmap" if index == 0 else part for index, part in enumerate(command)]

