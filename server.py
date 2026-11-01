from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from mcp.server.fastmcp import FastMCP

ROOT = Path(__file__).resolve().parent
CONFIG_FILE = ROOT / "pc-studio.config.json"


def load_config() -> dict[str, Any]:
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("La configuration doit être un objet JSON.")
        return data
    except FileNotFoundError:
        return {}


CONFIG = load_config()
PATHS = CONFIG.get("paths", {})
WORKSPACE = Path(
    os.environ.get("PC_STUDIO_WORKSPACE")
    or CONFIG.get("workspace")
    or (Path.home() / "PCStudioWorkspace")
).expanduser().resolve()
WORKSPACE.mkdir(parents=True, exist_ok=True)
COMFYUI_URL = (
    os.environ.get("COMFYUI_URL")
    or CONFIG.get("comfyui_url")
    or "http://127.0.0.1:8188"
).rstrip("/")

APP_CANDIDATES: dict[str, list[str]] = {
    "bforartists": [
        r"C:\Program Files\Bforartists\5.1.2\bforartists.exe",
        "bforartists.exe",
    ],
    "audacity": [
        r"C:\Program Files\Audacity\Audacity.exe",
        r"C:\Program Files (x86)\Audacity\Audacity.exe",
        "audacity.exe",
    ],
    "davinci_resolve": [
        r"C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe",
        "Resolve.exe",
    ],
    "fl_studio": [
        r"C:\Program Files\Image-Line\FL Studio 2026\FL64.exe",
        r"C:\Program Files\Image-Line\FL Studio 21\FL64.exe",
        "FL64.exe",
    ],
    "chrome": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        str(Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome/Application/chrome.exe"),
        "chrome.exe",
    ],
}

EXECUTABLE_CANDIDATES = {
    "ffmpeg": [r"C:\ProgramData\chocolatey\bin\ffmpeg.exe", "ffmpeg.exe"],
    "ffprobe": [r"C:\ProgramData\chocolatey\bin\ffprobe.exe", "ffprobe.exe"],
}


def find_executable(key: str, candidates: list[str]) -> str | None:
    configured = PATHS.get(key)
    choices = ([str(configured)] if configured else []) + candidates
    for choice in choices:
        if not choice:
            continue
        candidate = Path(choice).expanduser()
        if candidate.is_file():
            return str(candidate.resolve())
        found = shutil.which(choice)
        if found:
            return found
    return None


def app_path(name: str) -> str | None:
    if name not in APP_CANDIDATES:
        raise ValueError("Logiciel non autorisé. Consulte studio_status pour la liste.")
    return find_executable(name, APP_CANDIDATES[name])


def workspace_path(relative: str) -> Path:
    raw = Path(relative).expanduser()
    candidate = (raw if raw.is_absolute() else WORKSPACE / raw).resolve()
    if candidate != WORKSPACE and WORKSPACE not in candidate.parents:
        raise ValueError("Accès refusé : les fichiers doivent rester dans PCStudioWorkspace.")
    return candidate


def validate_local_comfyui() -> None:
    parsed = urlparse(COMFYUI_URL)
    if parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "localhost", "::1"):
        raise ValueError("ComfyUI doit utiliser une adresse HTTP locale (localhost).")


mcp = FastMCP("PC Studio Control")


@mcp.tool()
def studio_status() -> dict[str, Any]:
    """Affiche les logiciels détectés, leurs chemins et le dossier de travail."""
    apps = {name: app_path(name) for name in APP_CANDIDATES}
    tools = {
        name: find_executable(name, candidates)
        for name, candidates in EXECUTABLE_CANDIDATES.items()
    }
    return {
        "workspace": str(WORKSPACE),
        "applications": apps,
        "media_tools": tools,
        "comfyui_url": COMFYUI_URL,
        "config_file": str(CONFIG_FILE),
    }


@mcp.tool()
def list_workspace(path: str = ".") -> list[dict[str, Any]]:
    """Liste les fichiers et dossiers d'un sous-dossier de l'espace de travail."""
    folder = workspace_path(path)
    if not folder.exists():
        return []
    if not folder.is_dir():
        raise ValueError("Ce chemin n'est pas un dossier.")
    return [
        {
            "name": item.name,
            "is_dir": item.is_dir(),
            "size": item.stat().st_size if item.is_file() else None,
        }
        for item in sorted(folder.iterdir(), key=lambda item: (not item.is_dir(), item.name.casefold()))
    ]


@mcp.tool()
def read_text_file(path: str, max_chars: int = 20000) -> str:
    """Lit un fichier texte du workspace, avec une limite de taille."""
    file_path = workspace_path(path)
    if not file_path.is_file():
        raise FileNotFoundError("Fichier introuvable.")
    if file_path.stat().st_size > 250_000:
        raise ValueError("Fichier trop volumineux (250 Ko maximum).")
    return file_path.read_text(encoding="utf-8", errors="replace")[: max(1, min(max_chars, 20000))]


@mcp.tool()
def create_text_file(path: str, content: str) -> str:
    """Crée un fichier texte dans le workspace sans écraser un fichier existant."""
    file_path = workspace_path(path)
    if file_path.exists():
        raise FileExistsError("Le fichier existe déjà ; aucun écrasement effectué.")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("x", encoding="utf-8", newline="") as handle:
        handle.write(content)
    return f"Fichier créé : {file_path}"


@mcp.tool()
def create_project_folder(name: str) -> str:
    """Crée un dossier de projet directement dans le workspace."""
    if not name or name in (".", "..") or Path(name).is_absolute() or len(Path(name).parts) != 1:
        raise ValueError("Donne un nom de dossier simple, sans chemin.")
    target = workspace_path(name)
    target.mkdir(parents=True, exist_ok=False)
    return f"Dossier créé : {target}"


@mcp.tool()
def launch_app(name: str) -> str:
    """Lance un logiciel autorisé : Bforartists, Audacity, DaVinci Resolve ou FL Studio."""
    key = name.strip().lower().replace(" ", "_").replace("-", "_")
    if key == "resolve":
        key = "davinci_resolve"
    executable = app_path(key)
    if not executable:
        raise FileNotFoundError(f"{key} est introuvable. Vérifie son installation ou pc-studio.config.json.")
    subprocess.Popen(
        [executable],
        cwd=str(WORKSPACE),
        shell=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return f"{key} lancé."


@mcp.tool()
def open_chrome_guest(url: str = "") -> str:
    """Ouvre Google Chrome en mode Invité, avec une URL HTTP(S) facultative."""
    executable = app_path("chrome")
    if not executable:
        raise FileNotFoundError("Google Chrome est introuvable. Vérifie pc-studio.config.json.")
    args = [executable, "--guest"]
    if url.strip():
        parsed = urlparse(url.strip())
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("L'URL doit commencer par http:// ou https://.")
        args.append(url.strip())
    subprocess.Popen(
        args,
        cwd=str(WORKSPACE),
        shell=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return "Google Chrome a été ouvert en mode Invité."


@mcp.tool()
def ffmpeg_run(arguments: list[str]) -> str:
    """Lance FFmpeg sur des médias du workspace ; les entrées et sorties restent dans ce dossier."""
    executable = find_executable("ffmpeg", EXECUTABLE_CANDIDATES["ffmpeg"])
    if not executable:
        raise FileNotFoundError("FFmpeg est introuvable.")
    if len(arguments) < 3:
        raise ValueError("Fournis au minimum une entrée (-i fichier) et un fichier de sortie.")
    blocked = {
        "-y", "-filter_script", "-filter_complex_script", "-passlogfile",
        "-report", "-progress", "-dump_attachment", "-attach",
        "-protocol_whitelist", "-protocol_blacklist", "-init_hw_device",
    }
    if any(str(arg).lower() in blocked for arg in arguments):
        raise ValueError("Une option FFmpeg potentiellement dangereuse a été refusée.")

    safe_args: list[str] = ["-nostdin", "-n"]
    index = 0
    input_count = 0
    while index < len(arguments):
        arg = str(arguments[index])
        if arg == "-i":
            if index + 1 >= len(arguments):
                raise ValueError("Il manque le chemin après -i.")
            input_path = workspace_path(str(arguments[index + 1]))
            if not input_path.is_file():
                raise FileNotFoundError(f"Média introuvable : {input_path.name}")
            safe_args.extend(["-i", str(input_path)])
            input_count += 1
            index += 2
            continue
        if arg.startswith(("http://", "https://", "ftp://", "rtsp://")):
            raise ValueError("Les entrées réseau ne sont pas autorisées.")
        safe_args.append(arg)
        index += 1

    if input_count == 0:
        raise ValueError("Au moins une entrée locale avec -i est obligatoire.")
    output_path = workspace_path(str(arguments[-1]))
    if output_path == WORKSPACE or not output_path.suffix:
        raise ValueError("Le dernier argument doit être un fichier de sortie.")
    if output_path.exists():
        raise FileExistsError("Le fichier de sortie existe déjà.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    safe_args[-1] = str(output_path)

    result = subprocess.run(
        [executable, *safe_args],
        cwd=str(WORKSPACE),
        capture_output=True,
        text=True,
        timeout=600,
        shell=False,
    )
    log = (result.stdout + "\n" + result.stderr)[-10000:]
    return f"Code retour : {result.returncode}\n{log}"


@mcp.tool()
def ffprobe_file(path: str) -> str:
    """Récupère les informations techniques d'un fichier média du workspace."""
    executable = find_executable("ffprobe", EXECUTABLE_CANDIDATES["ffprobe"])
    if not executable:
        raise FileNotFoundError("FFprobe est introuvable.")
    media = workspace_path(path)
    if not media.is_file():
        raise FileNotFoundError("Fichier média introuvable dans le workspace.")
    result = subprocess.run(
        [executable, "-v", "error", "-show_format", "-show_streams", str(media)],
        cwd=str(WORKSPACE),
        capture_output=True,
        text=True,
        timeout=60,
        shell=False,
    )
    if result.returncode:
        raise RuntimeError((result.stderr or "FFprobe a échoué.")[-4000:])
    return result.stdout[:20000]


@mcp.tool()
def comfyui_status() -> dict[str, Any]:
    """Vérifie l'API locale ComfyUI sans déclencher de génération."""
    validate_local_comfyui()
    try:
        response = requests.get(COMFYUI_URL + "/system_stats", timeout=3)
        response.raise_for_status()
        return {"online": True, "url": COMFYUI_URL, "system": response.json()}
    except requests.RequestException as error:
        return {"online": False, "url": COMFYUI_URL, "error": str(error)}


if __name__ == "__main__":
    mcp.run(transport="stdio")
