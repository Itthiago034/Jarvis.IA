"""
JARVIS - System Automation Tools
================================
Ferramentas para automação do sistema Windows.
Controle de janelas, clipboard, processos, arquivos e mais.
"""

import os
import sys
import json
import shutil
import asyncio
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

# Windows-specific imports
if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes
    
    # Constantes do Windows
    SW_MINIMIZE = 6
    SW_MAXIMIZE = 3
    SW_RESTORE = 9
    SW_HIDE = 0
    SW_SHOW = 5


class WindowManager:
    """Gerenciador de janelas do Windows"""
    
    def __init__(self):
        if sys.platform != "win32":
            raise OSError("WindowManager só funciona no Windows")
        
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
    
    def get_all_windows(self) -> List[Dict[str, Any]]:
        """Lista todas as janelas visíveis"""
        windows = []
        
        def enum_callback(hwnd, _):
            if self.user32.IsWindowVisible(hwnd):
                length = self.user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    title = ctypes.create_unicode_buffer(length + 1)
                    self.user32.GetWindowTextW(hwnd, title, length + 1)
                    
                    # Obter nome do processo
                    pid = wintypes.DWORD()
                    self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    
                    windows.append({
                        "hwnd": hwnd,
                        "title": title.value,
                        "pid": pid.value
                    })
            return True
        
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        self.user32.EnumWindows(WNDENUMPROC(enum_callback), 0)
        
        return windows
    
    def find_window(self, title_contains: str) -> Optional[int]:
        """Encontra janela pelo título"""
        windows = self.get_all_windows()
        title_lower = title_contains.lower()
        
        for w in windows:
            if title_lower in w["title"].lower():
                return w["hwnd"]
        return None
    
    def focus_window(self, hwnd: int) -> bool:
        """Coloca janela em foco"""
        try:
            self.user32.SetForegroundWindow(hwnd)
            return True
        except Exception:
            return False
    
    def minimize_window(self, hwnd: int) -> bool:
        """Minimiza janela"""
        try:
            self.user32.ShowWindow(hwnd, SW_MINIMIZE)
            return True
        except Exception:
            return False
    
    def maximize_window(self, hwnd: int) -> bool:
        """Maximiza janela"""
        try:
            self.user32.ShowWindow(hwnd, SW_MAXIMIZE)
            return True
        except Exception:
            return False
    
    def restore_window(self, hwnd: int) -> bool:
        """Restaura janela"""
        try:
            self.user32.ShowWindow(hwnd, SW_RESTORE)
            return True
        except Exception:
            return False
    
    def close_window(self, hwnd: int) -> bool:
        """Fecha janela"""
        try:
            WM_CLOSE = 0x0010
            self.user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
            return True
        except Exception:
            return False
    
    def get_foreground_window(self) -> Dict[str, Any]:
        """Obtém janela em primeiro plano"""
        hwnd = self.user32.GetForegroundWindow()
        length = self.user32.GetWindowTextLengthW(hwnd)
        title = ctypes.create_unicode_buffer(length + 1)
        self.user32.GetWindowTextW(hwnd, title, length + 1)
        
        return {"hwnd": hwnd, "title": title.value}


class ClipboardManager:
    """Gerenciador de clipboard"""
    
    @staticmethod
    def get_text() -> str:
        """Obtém texto do clipboard"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-Clipboard"],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip()
        except Exception:
            return ""
    
    @staticmethod
    def set_text(text: str) -> bool:
        """Define texto no clipboard"""
        try:
            # Escapar aspas
            escaped = text.replace('"', '`"')
            subprocess.run(
                ["powershell", "-Command", f'Set-Clipboard -Value "{escaped}"'],
                capture_output=True, timeout=5
            )
            return True
        except Exception:
            return False
    
    @staticmethod
    def clear() -> bool:
        """Limpa clipboard"""
        try:
            subprocess.run(
                ["powershell", "-Command", "Set-Clipboard -Value $null"],
                capture_output=True, timeout=5
            )
            return True
        except Exception:
            return False


class ProcessManager:
    """Gerenciador de processos"""
    
    @staticmethod
    def list_processes() -> List[Dict[str, Any]]:
        """Lista processos em execução"""
        import psutil  # type: ignore[reportMissingImports]
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                processes.append({
                    "pid": info['pid'],
                    "name": info['name'],
                    "cpu": info['cpu_percent'],
                    "memory": info['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return sorted(processes, key=lambda x: x['memory'] or 0, reverse=True)[:50]
    
    @staticmethod
    def kill_process(pid: int) -> bool:
        """Encerra um processo"""
        import psutil  # type: ignore[reportMissingImports]
        
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Obtém informações do sistema"""
        import psutil  # type: ignore[reportMissingImports]
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_percent": cpu_percent,
            "memory_total_gb": round(memory.total / (1024**3), 2),
            "memory_used_gb": round(memory.used / (1024**3), 2),
            "memory_percent": memory.percent,
            "disk_total_gb": round(disk.total / (1024**3), 2),
            "disk_used_gb": round(disk.used / (1024**3), 2),
            "disk_percent": disk.percent
        }


class FileManager:
    """Gerenciador de arquivos avançado"""
    
    @staticmethod
    def search_files(directory: str, pattern: str, recursive: bool = True) -> List[str]:
        """Busca arquivos por padrão"""
        path = Path(directory)
        if not path.exists():
            return []
        
        if recursive:
            return [str(f) for f in path.rglob(pattern)][:100]
        else:
            return [str(f) for f in path.glob(pattern)][:100]
    
    @staticmethod
    def organize_files(source_dir: str, rules: Dict[str, List[str]]) -> Dict[str, int]:
        """
        Organiza arquivos por extensão.
        rules: {"Imagens": [".jpg", ".png"], "Documentos": [".pdf", ".docx"]}
        """
        source = Path(source_dir)
        if not source.exists():
            return {"error": "Diretório não existe"}
        
        moved = {}
        for file in source.iterdir():
            if file.is_file():
                ext = file.suffix.lower()
                for folder, extensions in rules.items():
                    if ext in extensions:
                        dest_folder = source / folder
                        dest_folder.mkdir(exist_ok=True)
                        dest_file = dest_folder / file.name
                        
                        # Evitar sobrescrever
                        if dest_file.exists():
                            base = file.stem
                            counter = 1
                            while dest_file.exists():
                                dest_file = dest_folder / f"{base}_{counter}{ext}"
                                counter += 1
                        
                        shutil.move(str(file), str(dest_file))
                        moved[folder] = moved.get(folder, 0) + 1
                        break
        
        return moved
    
    @staticmethod
    def get_folder_size(directory: str) -> Dict[str, Any]:
        """Calcula tamanho de uma pasta"""
        path = Path(directory)
        if not path.exists():
            return {"error": "Diretório não existe"}
        
        total_size = 0
        file_count = 0
        folder_count = 0
        
        for item in path.rglob("*"):
            if item.is_file():
                total_size += item.stat().st_size
                file_count += 1
            elif item.is_dir():
                folder_count += 1
        
        return {
            "path": str(path),
            "size_bytes": total_size,
            "size_mb": round(total_size / (1024**2), 2),
            "size_gb": round(total_size / (1024**3), 2),
            "files": file_count,
            "folders": folder_count
        }
    
    @staticmethod
    def find_large_files(directory: str, min_size_mb: int = 100) -> List[Dict]:
        """Encontra arquivos grandes"""
        path = Path(directory)
        if not path.exists():
            return []
        
        min_size = min_size_mb * 1024 * 1024
        large_files = []
        
        for file in path.rglob("*"):
            if file.is_file():
                try:
                    size = file.stat().st_size
                    if size >= min_size:
                        large_files.append({
                            "path": str(file),
                            "size_mb": round(size / (1024**2), 2),
                            "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                        })
                except Exception:
                    pass
        
        return sorted(large_files, key=lambda x: x['size_mb'], reverse=True)[:50]
    
    @staticmethod
    def find_duplicate_files(directory: str) -> List[List[str]]:
        """Encontra arquivos duplicados (por tamanho e nome)"""
        import hashlib
        
        path = Path(directory)
        if not path.exists():
            return []
        
        # Agrupar por tamanho
        size_map: Dict[int, List[Path]] = {}
        for file in path.rglob("*"):
            if file.is_file():
                try:
                    size = file.stat().st_size
                    if size > 0:
                        if size not in size_map:
                            size_map[size] = []
                        size_map[size].append(file)
                except Exception:
                    pass
        
        # Verificar hash para arquivos do mesmo tamanho
        duplicates = []
        for size, files in size_map.items():
            if len(files) > 1:
                hash_map: Dict[str, List[str]] = {}
                for file in files[:20]:  # Limitar para não demorar
                    try:
                        with open(file, 'rb') as f:
                            file_hash = hashlib.md5(f.read(8192)).hexdigest()
                        if file_hash not in hash_map:
                            hash_map[file_hash] = []
                        hash_map[file_hash].append(str(file))
                    except Exception:
                        pass
                
                for h, paths in hash_map.items():
                    if len(paths) > 1:
                        duplicates.append(paths)
        
        return duplicates[:20]


class AppLauncher:
    """Lançador de aplicativos"""
    
    # Mapeamento de nomes amigáveis para executáveis
    APPS = {
        # Navegadores
        "chrome": "chrome.exe",
        "firefox": "firefox.exe",
        "edge": "msedge.exe",
        "brave": "brave.exe",
        
        # Editores
        "vscode": "code.exe",
        "notepad": "notepad.exe",
        "notepad++": "notepad++.exe",
        
        # Comunicação
        "discord": "Discord.exe",
        "slack": "slack.exe",
        "teams": "ms-teams.exe",
        "telegram": "Telegram.exe",
        
        # Mídia
        "spotify": "Spotify.exe",
        "vlc": "vlc.exe",
        
        # Utilitários
        "explorer": "explorer.exe",
        "terminal": "wt.exe",
        "cmd": "cmd.exe",
        "powershell": "powershell.exe",
        "calc": "calc.exe",
        
        # Desenvolvimento
        "docker": "Docker Desktop.exe",
        "postman": "Postman.exe",
        "git-gui": "git-gui.exe",
    }
    
    @classmethod
    def launch(cls, app_name: str, args: str = "") -> bool:
        """Abre um aplicativo"""
        app_lower = app_name.lower()
        
        # Verificar se é um nome conhecido
        executable = cls.APPS.get(app_lower, app_name)
        
        try:
            if args:
                subprocess.Popen(f'start "" "{executable}" {args}', shell=True)
            else:
                subprocess.Popen(f'start "" "{executable}"', shell=True)
            return True
        except Exception:
            return False
    
    @classmethod
    def open_url(cls, url: str) -> bool:
        """Abre URL no navegador padrão"""
        try:
            import webbrowser
            webbrowser.open(url)
            return True
        except Exception:
            return False
    
    @classmethod
    def open_folder(cls, path: str) -> bool:
        """Abre pasta no Explorer"""
        try:
            os.startfile(path)
            return True
        except Exception:
            return False


class ThemeManager:
    """Gerenciador de tema do Windows"""
    
    @staticmethod
    def get_current_theme() -> str:
        """Obtém tema atual (light/dark)"""
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return "light" if value == 1 else "dark"
        except Exception:
            return "unknown"
    
    @staticmethod
    def set_theme(theme: str) -> bool:
        """Define tema (light/dark)"""
        try:
            import winreg
            value = 1 if theme.lower() == "light" else 0
            
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, value)
            winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, value)
            winreg.CloseKey(key)
            return True
        except Exception:
            return False
    
    @staticmethod
    def toggle_theme() -> str:
        """Alterna entre light e dark"""
        current = ThemeManager.get_current_theme()
        new_theme = "light" if current == "dark" else "dark"
        ThemeManager.set_theme(new_theme)
        return new_theme


# ==================== FUNÇÕES DE FERRAMENTA PARA O AGENTE ====================

def get_system_tools():
    """Retorna as ferramentas de sistema para o CodeAgent"""
    
    # Inicializar managers (apenas no Windows)
    if sys.platform == "win32":
        window_mgr = WindowManager()
    else:
        window_mgr = None
    
    clipboard = ClipboardManager()
    process_mgr = ProcessManager()
    file_mgr = FileManager()
    launcher = AppLauncher()
    theme_mgr = ThemeManager()
    
    async def list_windows() -> str:
        """
        Lista todas as janelas abertas no sistema.
        
        Returns:
            Lista de janelas com título e ID
        """
        if not window_mgr:
            return "Funcionalidade disponível apenas no Windows"
        
        windows = window_mgr.get_all_windows()
        if not windows:
            return "Nenhuma janela encontrada"
        
        result = ["🪟 Janelas abertas:\n"]
        for w in windows[:30]:
            result.append(f"  [{w['hwnd']}] {w['title']}")
        return "\n".join(result)
    
    async def focus_window(title: str) -> str:
        """
        Coloca uma janela em foco pelo título.
        
        Args:
            title: Parte do título da janela
        
        Returns:
            Confirmação da ação
        """
        if not window_mgr:
            return "Funcionalidade disponível apenas no Windows"
        
        hwnd = window_mgr.find_window(title)
        if hwnd:
            window_mgr.focus_window(hwnd)
            return f"✅ Janela '{title}' colocada em foco"
        return f"❌ Janela '{title}' não encontrada"
    
    async def minimize_all_windows() -> str:
        """
        Minimiza todas as janelas (mostrar área de trabalho).
        
        Returns:
            Confirmação
        """
        if sys.platform != "win32":
            return "Funcionalidade disponível apenas no Windows"
        
        try:
            ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)  # Win key down
            ctypes.windll.user32.keybd_event(0x44, 0, 0, 0)  # D key down
            ctypes.windll.user32.keybd_event(0x44, 0, 2, 0)  # D key up
            ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)  # Win key up
            return "✅ Todas as janelas minimizadas"
        except Exception as e:
            return f"❌ Erro: {e}"
    
    async def get_clipboard() -> str:
        """
        Obtém o conteúdo atual do clipboard.
        
        Returns:
            Texto do clipboard
        """
        text = clipboard.get_text()
        if text:
            return f"📋 Clipboard:\n{text[:2000]}"
        return "📋 Clipboard vazio"
    
    async def set_clipboard(text: str) -> str:
        """
        Define texto no clipboard.
        
        Args:
            text: Texto a copiar
        
        Returns:
            Confirmação
        """
        if clipboard.set_text(text):
            return "✅ Texto copiado para o clipboard"
        return "❌ Erro ao copiar para clipboard"
    
    async def system_status() -> str:
        """
        Mostra status do sistema (CPU, RAM, Disco).
        
        Returns:
            Informações do sistema
        """
        info = process_mgr.get_system_info()
        
        return (
            f"💻 **Status do Sistema**\n\n"
            f"🔲 CPU: {info['cpu_percent']}%\n"
            f"🧠 RAM: {info['memory_used_gb']:.1f}GB / {info['memory_total_gb']:.1f}GB ({info['memory_percent']}%)\n"
            f"💾 Disco: {info['disk_used_gb']:.1f}GB / {info['disk_total_gb']:.1f}GB ({info['disk_percent']}%)"
        )
    
    async def list_processes(top: int = 20) -> str:
        """
        Lista processos consumindo mais recursos.
        
        Args:
            top: Número de processos a mostrar
        
        Returns:
            Lista de processos
        """
        processes = process_mgr.list_processes()[:top]
        
        result = ["⚙️ Processos (por uso de memória):\n"]
        for p in processes:
            memory = p['memory'] or 0
            cpu = p['cpu'] or 0
            result.append(f"  [{p['pid']}] {p['name']}: RAM {memory:.1f}% | CPU {cpu:.1f}%")
        
        return "\n".join(result)
    
    async def kill_process(pid: int) -> str:
        """
        Encerra um processo pelo PID.
        
        Args:
            pid: ID do processo
        
        Returns:
            Confirmação
        """
        if process_mgr.kill_process(pid):
            return f"✅ Processo {pid} encerrado"
        return f"❌ Não foi possível encerrar o processo {pid}"
    
    async def open_app(app_name: str) -> str:
        """
        Abre um aplicativo.
        
        Args:
            app_name: Nome do app (chrome, vscode, discord, spotify, etc)
        
        Returns:
            Confirmação
        """
        if launcher.launch(app_name):
            return f"✅ Abrindo {app_name}..."
        return f"❌ Não foi possível abrir {app_name}"
    
    async def open_url(url: str) -> str:
        """
        Abre uma URL no navegador padrão.
        
        Args:
            url: URL a abrir
        
        Returns:
            Confirmação
        """
        if launcher.open_url(url):
            return f"✅ Abrindo {url}..."
        return f"❌ Erro ao abrir URL"
    
    async def open_folder(path: str) -> str:
        """
        Abre uma pasta no explorador de arquivos.
        
        Args:
            path: Caminho da pasta
        
        Returns:
            Confirmação
        """
        if Path(path).exists():
            if launcher.open_folder(path):
                return f"✅ Abrindo pasta {path}..."
            return "❌ Erro ao abrir pasta"
        return f"❌ Pasta não existe: {path}"
    
    async def search_files(directory: str, pattern: str) -> str:
        """
        Busca arquivos em um diretório.
        
        Args:
            directory: Diretório inicial
            pattern: Padrão de busca (ex: "*.py", "*.pdf")
        
        Returns:
            Lista de arquivos encontrados
        """
        files = file_mgr.search_files(directory, pattern)
        if not files:
            return f"Nenhum arquivo '{pattern}' encontrado em {directory}"
        
        result = [f"📁 Arquivos '{pattern}' em {directory}:\n"]
        for f in files[:30]:
            result.append(f"  • {f}")
        
        if len(files) > 30:
            result.append(f"\n  ... e mais {len(files) - 30} arquivos")
        
        return "\n".join(result)
    
    async def organize_downloads() -> str:
        """
        Organiza a pasta Downloads por tipo de arquivo.
        
        Returns:
            Relatório da organização
        """
        downloads = str(Path.home() / "Downloads")
        
        rules = {
            "Imagens": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
            "Documentos": [".pdf", ".doc", ".docx", ".txt", ".xlsx", ".pptx", ".odt"],
            "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv"],
            "Musicas": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
            "Arquivos": [".zip", ".rar", ".7z", ".tar", ".gz"],
            "Executaveis": [".exe", ".msi", ".dmg"],
            "Codigo": [".py", ".js", ".html", ".css", ".json", ".xml"]
        }
        
        moved = file_mgr.organize_files(downloads, rules)
        
        if "error" in moved:
            return f"❌ {moved['error']}"
        
        if not moved:
            return "📁 Nenhum arquivo para organizar em Downloads"
        
        result = ["✅ Downloads organizados:\n"]
        for folder, count in moved.items():
            result.append(f"  📂 {folder}: {count} arquivo(s)")
        
        return "\n".join(result)
    
    async def find_large_files(directory: str, min_size_mb: int = 100) -> str:
        """
        Encontra arquivos grandes em um diretório.
        
        Args:
            directory: Diretório a buscar
            min_size_mb: Tamanho mínimo em MB
        
        Returns:
            Lista de arquivos grandes
        """
        files = file_mgr.find_large_files(directory, min_size_mb)
        if not files:
            return f"Nenhum arquivo maior que {min_size_mb}MB em {directory}"
        
        result = [f"📦 Arquivos grandes (>{min_size_mb}MB) em {directory}:\n"]
        for f in files[:20]:
            result.append(f"  • {f['path']}\n    {f['size_mb']}MB - modificado: {f['modified'][:10]}")
        
        return "\n".join(result)
    
    async def toggle_dark_mode() -> str:
        """
        Alterna entre modo claro e escuro do Windows.
        
        Returns:
            Novo tema ativo
        """
        new_theme = theme_mgr.toggle_theme()
        emoji = "🌙" if new_theme == "dark" else "☀️"
        return f"{emoji} Tema alterado para: {new_theme}"
    
    async def get_theme() -> str:
        """
        Obtém o tema atual do Windows.
        
        Returns:
            Tema atual (light/dark)
        """
        theme = theme_mgr.get_current_theme()
        emoji = "🌙" if theme == "dark" else "☀️"
        return f"{emoji} Tema atual: {theme}"
    
    return {
        "list_windows": list_windows,
        "focus_window": focus_window,
        "minimize_all_windows": minimize_all_windows,
        "get_clipboard": get_clipboard,
        "set_clipboard": set_clipboard,
        "system_status": system_status,
        "list_processes": list_processes,
        "kill_process": kill_process,
        "open_app": open_app,
        "open_url": open_url,
        "open_folder": open_folder,
        "search_files": search_files,
        "organize_downloads": organize_downloads,
        "find_large_files": find_large_files,
        "toggle_dark_mode": toggle_dark_mode,
        "get_theme": get_theme,
    }
