# PC Studio Control

Agent local Windows pour orchestrer un studio créatif depuis un hôte compatible MCP.

> **Prototype testable 0.1.0.** Ce dépôt fournit un serveur MCP local et un lanceur Windows. Il ne crée pas de tunnel Internet et ne donne pas à ChatGPT Web un accès direct au PC : l'application hôte doit pouvoir démarrer un serveur MCP local (stdio).

## Fonctionnalités
- Inventaire de FFmpeg, FFprobe, Blender, Audacity et ComfyUI.
- Ouvrir Blender et Audacity.
- Lire/lister/créer des fichiers dans un espace de travail dédié.
- Exécuter FFmpeg avec garde-fous et sans écrasement forcé.
- Vérifier ComfyUI via son API locale.
- Créer des dossiers de projet.

## Installation Windows
1. Installer Python 3.11 ou plus récent.
2. Télécharger/cloner ce dépôt.
3. Double-cliquer sur `INSTALL.bat`.
4. Lancer `START.bat` pour vérifier les dépendances.
5. Dans un client MCP compatible, enregistrer le serveur comme décrit dans `mcp.example.json`, en remplaçant le chemin par le chemin absolu du dépôt.

Le serveur MCP utilise **stdio** : il est démarré par le client MCP, pas par un service distant.

## Configuration
- `PC_STUDIO_WORKSPACE` : dossier de travail (défaut : `%USERPROFILE%\\PCStudioWorkspace`).
- `COMFYUI_URL` : URL locale de ComfyUI (défaut : `http://127.0.0.1:8188`).

## Outils MCP
`studio_status`, `list_workspace`, `read_text_file`, `create_text_file`, `create_project_folder`, `launch_app`, `ffmpeg_run`, `comfyui_status`.

## Sécurité et limites
- Aucun shell générique / PowerShell arbitraire.
- Aucun accès aux mots de passe, cookies, profils navigateur, clés privées ou dossiers hors workspace.
- Pas de suppression ni d'écrasement de fichiers existants.
- FFmpeg est limité au workspace et ne peut pas utiliser `-y`.
- Publication, envoi, achat, installation et suppression restent des actions distinctes.
- Contrôle souris/clavier universel et capture d'écran non inclus dans cette version.

## Dépannage
- Python introuvable : installer Python 3.11+ et cocher “Add Python to PATH”.
- FFmpeg introuvable : installer FFmpeg puis ajouter son dossier `bin` au PATH.
- ComfyUI hors ligne : démarrer ComfyUI localement et vérifier `COMFYUI_URL`.
- Le client MCP ne démarre pas le serveur : vérifier le chemin absolu vers `server.py`.

Licence : MIT.
