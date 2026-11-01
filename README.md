# PC Studio Control

Serveur MCP local pour piloter les logiciels créatifs installés sur ton PC Windows depuis un client compatible MCP (ChatGPT Desktop/Codex, GitHub Copilot dans VS Code (y compris Copilot Free) ou ZCode Desktop).

## Fonctions

- Détection des logiciels et chemins d'installation.
- Lancement de **Bforartists**, **Audacity**, **DaVinci Resolve** et **FL Studio**.
- Ouverture de **Google Chrome en mode Invité**, avec URL HTTP(S) facultative.
- **FFmpeg** : traitement de médias locaux dans l'espace de travail, sans écrasement.
- **FFprobe** : lecture des métadonnées d'un média.
- **ComfyUI** : vérification de l'API locale.
- Création, lecture et liste de fichiers dans le workspace.

## Configuration incluse pour ce PC

Le fichier `pc-studio.config.json` contient les chemins Windows communiqués pour ce PC :

- Python 3.11 : `C:\Program Files\Python311\python.exe`
- Workspace : `C:\Users\7erro\PCStudioWorkspace`
- Dépôt : `C:\Users\7erro\OneDrive\Documents\Codage\pcstudiocontrolchatgpt`
- Bforartists, Audacity, DaVinci Resolve, FL Studio 2026, FFmpeg, FFprobe et Chrome.

Ces chemins sont des paramètres locaux à cette machine. Si tu déplaces le dépôt ou réinstalles un logiciel, modifie `pc-studio.config.json` et les fichiers de configuration du client.

> Le dépôt étant privé, la configuration de chemins demandée est versionnée. Ne place jamais de mot de passe, cookie, jeton OAuth, clé API ou secret dans Git, même dans un dépôt privé.

## Installation

1. Installer Python 3.11+.
2. Cloner le dépôt.
3. Lancer `INSTALL.bat`.
4. Lancer `START.bat` pour vérifier l'environnement.
5. Ajouter le serveur MCP à ton client avec le fichier de configuration correspondant.

## ChatGPT Desktop / Codex

Le fichier `client-config/chatgpt-codex.toml` contient le bloc TOML à ajouter à `%USERPROFILE%\.codex\config.toml` :

```toml
[mcp_servers.pc_studio_control]
command = 'C:\Program Files\Python311\python.exe'
args = ['C:\Users\7erro\OneDrive\Documents\Codage\pcstudiocontrolchatgpt\server.py']
```

Redémarre le client après modification et vérifie que le serveur MCP apparaît dans la liste des serveurs connectés. La disponibilité du MCP local dépend du client et de son mode d'exécution local ; ChatGPT Web dans un navigateur ne peut pas démarrer directement un processus sur ce PC.

## Visual Studio Code / GitHub Copilot (y compris Copilot Free)

Le dépôt inclut `.vscode/mcp.json`. VS Code détecte automatiquement ce fichier à l'ouverture du dépôt et peut démarrer le serveur MCP local pour Copilot.

**Configuration prévue pour ce PC :**
- Python : `C:\\Program Files\\Python311\\python.exe`
- Script : `${workspaceFolder}\\server.py` (chemin relatif au dépôt, donc le dossier du dépôt peut être déplacé)
- Workspace : `C:\\Users\\7erro\\PCStudioWorkspace`

**Activation dans VS Code :**
1. Ouvre le dossier du dépôt dans VS Code.
2. Ouvre le fichier `.vscode/mcp.json` et clique sur **Start** en haut du fichier, ou utilise la palette de commandes `Ctrl+Shift+P` puis **MCP: List Servers**.
3. Accepte le démarrage du serveur local lorsque VS Code le demande.
4. Ouvre Copilot Chat et sélectionne le mode **Agent**.
5. Ouvre le sélecteur d'outils et vérifie que **pcStudioControl** apparaît. Active ses outils.
6. Essaie : « Utilise PC Studio Control pour afficher les logiciels disponibles », puis « Ouvre Audacity ».

**Copilot Free :** le support MCP de VS Code est disponible sur les forfaits Copilot, y compris Free. Le forfait gratuit conserve toutefois ses propres limites d'utilisation de Copilot ; PC Studio Control ne les augmente pas. Il faut une version récente de VS Code (1.99 ou ultérieure) et une session Copilot connectée.

Le serveur tourne localement sur ton PC via Python ; aucune clé API Copilot n'est à ajouter au dépôt. Ne publie jamais de jeton, mot de passe ou cookie.

## ZCode Desktop

Importer ou recopier `client-config/zcode-mcp.json` dans les paramètres **MCP Servers** de ZCode. Le transport est `stdio`. Redémarre ZCode après l'ajout.

## Outils MCP

| Outil | Utilité |
|---|---|
| `studio_status` | Détecte les applications, outils média et chemins |
| `launch_app` | Lance un logiciel autorisé |
| `open_chrome_guest` | Ouvre Chrome en mode Invité, avec URL facultative |
| `list_workspace` | Liste un dossier de travail |
| `read_text_file` | Lit un fichier texte |
| `create_text_file` | Crée un fichier sans écrasement |
| `create_project_folder` | Crée un dossier de projet |
| `ffmpeg_run` | Traite des médias locaux dans le workspace |
| `ffprobe_file` | Lit les métadonnées d'un média |
| `comfyui_status` | Vérifie ComfyUI sur localhost |

### Exemples de demandes

- « Ouvre Bforartists. »
- « Ouvre Chrome en invité sur https://example.com. »
- « Vérifie si ComfyUI est lancé. »
- « Liste les fichiers de mon workspace. »
- « Donne les informations techniques de video.mp4. »

## Sécurité

- Pas de shell générique, PowerShell arbitraire ou lancement de chemin d'exécutable fourni par l'utilisateur.
- Les applications sont limitées à une liste autorisée.
- Chrome est lancé avec `--guest` ; aucun cookie ou profil de navigation n'est lu par le serveur.
- Les opérations de fichiers sont limitées à `PCStudioWorkspace`.
- FFmpeg n'autorise pas les entrées réseau et n'écrase pas les sorties existantes.
- ComfyUI doit rester accessible via localhost.
- Aucun mot de passe, cookie, token ou secret ne doit être ajouté au dépôt.

## Dépannage

- **Application introuvable** : vérifie le chemin correspondant dans `pc-studio.config.json`.
- **Chrome absent** : installe Chrome ou corrige son chemin dans la configuration.
- **FFmpeg/FFprobe absents** : vérifie le chemin Chocolatey et l'installation.
- **ComfyUI hors ligne** : démarre ComfyUI et vérifie `http://127.0.0.1:8188`.
- **MCP non connecté** : vérifie les chemins absolus Python et `server.py`, puis redémarre le client.

Licence : MIT.
