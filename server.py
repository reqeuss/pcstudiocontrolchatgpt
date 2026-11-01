from __future__ import annotations
import os, shutil, subprocess
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("PC Studio Control")
WORKSPACE = Path(os.environ.get("PC_STUDIO_WORKSPACE", str(Path.home() / "PCStudioWorkspace"))).expanduser().resolve()
WORKSPACE.mkdir(parents=True, exist_ok=True)
COMFYUI_URL = os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188").rstrip("/")
APP_COMMANDS = {"blender": "blender", "audacity": "audacity"}

def workspace_path(relative: str) -> Path:
    candidate = (WORKSPACE / relative).resolve()
    if candidate != WORKSPACE and WORKSPACE not in candidate.parents:
        raise ValueError("Accès refusé : chemin limité à PCStudioWorkspace.")
    return candidate

@mcp.tool()
def studio_status() -> dict[str, Any]:
    """Détecte les logiciels créatifs disponibles et indique le workspace."""
    return {"workspace": str(WORKSPACE), "applications": {
        "ffmpeg": shutil.which("ffmpeg"), "ffprobe": shutil.which("ffprobe"),
        "blender": shutil.which("blender"), "audacity": shutil.which("audacity"),
        "comfyui": "API locale (voir comfyui_status)"
    }, "comfyui_url": COMFYUI_URL}

@mcp.tool()
def list_workspace(path: str = ".") -> list[dict[str, Any]]:
    """Liste un sous-dossier du workspace."""
    folder = workspace_path(path)
    if not folder.exists(): return []
    if not folder.is_dir(): raise ValueError("Ce chemin n'est pas un dossier.")
    return [{"name": p.name, "is_dir": p.is_dir(), "size": p.stat().st_size if p.is_file() else None}
            for p in sorted(folder.iterdir(), key=lambda x: (not x.is_dir(), x.name.casefold()))]

@mcp.tool()
def read_text_file(path: str, max_chars: int = 20000) -> str:
    """Lit un fichier texte du workspace (maximum 20 000 caractères)."""
    p = workspace_path(path)
    if not p.is_file(): raise FileNotFoundError("Fichier introuvable.")
    if p.stat().st_size > 250_000: raise ValueError("Fichier trop volumineux.")
    return p.read_text(encoding="utf-8", errors="replace")[:max(1, min(max_chars, 20000))]

@mcp.tool()
def create_text_file(path: str, content: str) -> str:
    """Crée un fichier texte sans écraser un fichier existant."""
    p = workspace_path(path)
    if p.exists(): raise FileExistsError("Le fichier existe déjà ; aucun écrasement.")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Fichier créé : {p}"

@mcp.tool()
def create_project_folder(name: str) -> str:
    """Crée un nouveau dossier de projet dans le workspace."""
    if not name or name in (".", "..") or Path(name).is_absolute() or len(Path(name).parts) != 1:
        raise ValueError("Donne un nom simple, sans chemin.")
    target = workspace_path(name)
    target.mkdir(parents=True, exist_ok=False)
    return f"Dossier créé : {target}"

@mcp.tool()
def launch_app(name: str) -> str:
    """Ouvre Blender ou Audacity s'ils sont installés et présents dans PATH."""
    key = name.strip().lower()
    if key not in APP_COMMANDS: raise ValueError("Applications autorisées : blender, audacity.")
    exe = shutil.which(APP_COMMANDS[key])
    if not exe: raise FileNotFoundError(f"{key} introuvable dans PATH.")
    subprocess.Popen([exe], cwd=str(WORKSPACE), shell=False,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return f"{key} lancé."

@mcp.tool()
def ffmpeg_run(arguments: list[str]) -> str:
    """Exécute FFmpeg sur les médias du workspace, sans écrasement forcé."""
    exe = shutil.which("ffmpeg")
    if not exe: raise FileNotFoundError("FFmpeg introuvable dans PATH.")
    if not arguments: raise ValueError("Arguments manquants.")
    if any(a in ("-y", "-n", "-filter_script", "-passlogfile") for a in arguments):
        raise ValueError("Option FFmpeg refusée.")
    safe = []
    for arg in arguments:
        value = str(arg)
        if value.startswith("-"): safe.append(value); continue
        if "/" in value or "\\\\" in value or Path(value).suffix:
            p = workspace_path(value)
            if p.is_dir(): raise ValueError("Un dossier ne peut pas être un fichier média.")
            safe.append(str(p))
        else: safe.append(value)
    output = Path(safe[-1])
    if output.suffix and output.exists(): raise FileExistsError("La sortie existe déjà.")
    result = subprocess.run([exe, *safe], cwd=str(WORKSPACE), capture_output=True,
                             text=True, timeout=600, shell=False)
    return f"Code retour : {result.returncode}\\n{(result.stdout + chr(10) + result.stderr)[-10000:]}"

@mcp.tool()
def comfyui_status() -> dict[str, Any]:
    """Vérifie l'API locale ComfyUI sans lancer de génération."""
    parsed = urlparse(COMFYUI_URL)
    if parsed.hostname not in ("127.0.0.1", "localhost", "::1"):
        raise ValueError("ComfyUI doit rester configuré sur localhost.")
    try:
        r = requests.get(COMFYUI_URL + "/system_stats", timeout=3)
        r.raise_for_status()
        return {"online": True, "url": COMFYUI_URL, "system": r.json()}
    except requests.RequestException as e:
        return {"online": False, "url": COMFYUI_URL, "error": str(e)}

if __name__ == "__main__":
    mcp.run(transport="stdio")
