"""
JARVIS CLI - Context Detection
==============================
Detecta automaticamente o contexto do projeto atual.
"""

import os
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import json


@dataclass
class ProjectContext:
    """Contexto do projeto atual"""
    root_path: Path
    project_type: Optional[str] = None
    language: Optional[str] = None
    framework: Optional[str] = None
    git_branch: Optional[str] = None
    git_status: Optional[Dict[str, Any]] = None
    recent_files: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def to_prompt_context(self) -> str:
        """Converte contexto para texto a ser incluído no prompt"""
        lines = ["## Contexto do Projeto\n"]
        
        lines.append(f"**Diretório:** `{self.root_path}`")
        
        if self.project_type:
            lines.append(f"**Tipo:** {self.project_type}")
        
        if self.language:
            lines.append(f"**Linguagem:** {self.language}")
            
        if self.framework:
            lines.append(f"**Framework:** {self.framework}")
        
        if self.git_branch:
            lines.append(f"**Branch Git:** `{self.git_branch}`")
        
        if self.git_status:
            modified = self.git_status.get("modified", [])
            staged = self.git_status.get("staged", [])
            if modified:
                lines.append(f"**Arquivos modificados:** {len(modified)}")
            if staged:
                lines.append(f"**Arquivos staged:** {len(staged)}")
        
        if self.recent_files:
            lines.append(f"\n**Arquivos recentes:**")
            for f in self.recent_files[:5]:
                lines.append(f"  - `{f}`")
        
        if self.errors:
            lines.append(f"\n**Erros detectados:** {len(self.errors)}")
        
        return "\n".join(lines)


class ContextDetector:
    """Detecta contexto do projeto automaticamente"""
    
    # Arquivos que indicam tipo de projeto
    PROJECT_INDICATORS = {
        "python": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
        "node": ["package.json", "yarn.lock", "pnpm-lock.yaml"],
        "rust": ["Cargo.toml", "Cargo.lock"],
        "go": ["go.mod", "go.sum"],
        "java": ["pom.xml", "build.gradle", "build.gradle.kts"],
        "dotnet": ["*.csproj", "*.sln", "*.fsproj"],
        "php": ["composer.json", "composer.lock"],
        "ruby": ["Gemfile", "Gemfile.lock"],
    }
    
    # Frameworks detectáveis
    FRAMEWORK_INDICATORS = {
        "django": ["manage.py", "django"],
        "flask": ["flask"],
        "fastapi": ["fastapi"],
        "react": ["react", "react-dom"],
        "vue": ["vue"],
        "angular": ["@angular/core"],
        "nextjs": ["next"],
        "express": ["express"],
        "nestjs": ["@nestjs/core"],
        "livekit": ["livekit", "livekit-agents"],
    }
    
    def __init__(self, path: Optional[str] = None):
        self.path = Path(path) if path else Path.cwd()
    
    def detect(self) -> ProjectContext:
        """Detecta todo o contexto do projeto"""
        context = ProjectContext(root_path=self.path)
        
        # Detectar tipo de projeto e linguagem
        self._detect_project_type(context)
        
        # Detectar framework
        self._detect_framework(context)
        
        # Detectar Git
        self._detect_git(context)
        
        # Listar arquivos recentes
        self._detect_recent_files(context)
        
        return context
    
    def _detect_project_type(self, context: ProjectContext):
        """Detecta o tipo de projeto baseado em arquivos"""
        for lang, indicators in self.PROJECT_INDICATORS.items():
            for indicator in indicators:
                if "*" in indicator:
                    # Pattern glob
                    if list(self.path.glob(indicator)):
                        context.language = lang
                        context.project_type = f"Projeto {lang.capitalize()}"
                        return
                else:
                    # Arquivo específico
                    if (self.path / indicator).exists():
                        context.language = lang
                        context.project_type = f"Projeto {lang.capitalize()}"
                        return
    
    def _detect_framework(self, context: ProjectContext):
        """Detecta framework baseado em dependências"""
        deps_content = ""
        
        # Ler arquivo de dependências baseado na linguagem
        if context.language == "python":
            for deps_file in ["requirements.txt", "pyproject.toml", "Pipfile"]:
                deps_path = self.path / deps_file
                if deps_path.exists():
                    try:
                        deps_content = deps_path.read_text(encoding="utf-8").lower()
                        break
                    except Exception:
                        pass
        
        elif context.language == "node":
            package_json = self.path / "package.json"
            if package_json.exists():
                try:
                    data = json.loads(package_json.read_text(encoding="utf-8"))
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                    deps_content = " ".join(deps.keys()).lower()
                    context.dependencies = list(deps.keys())[:20]
                except Exception:
                    pass
        
        # Detectar framework
        for framework, keywords in self.FRAMEWORK_INDICATORS.items():
            for keyword in keywords:
                if keyword.lower() in deps_content:
                    context.framework = framework.capitalize()
                    return
    
    def _detect_git(self, context: ProjectContext):
        """Detecta informações do Git"""
        git_dir = self.path / ".git"
        if not git_dir.exists():
            return
        
        try:
            # Branch atual
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                context.git_branch = result.stdout.strip()
            
            # Status
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
                staged = [l[3:] for l in lines if l and l[0] in "MADRCU"]
                modified = [l[3:] for l in lines if l and l[1] in "MADRCU"]
                untracked = [l[3:] for l in lines if l and l.startswith("??")]
                
                context.git_status = {
                    "staged": staged,
                    "modified": modified,
                    "untracked": untracked
                }
        except Exception:
            pass
    
    def _detect_recent_files(self, context: ProjectContext):
        """Lista arquivos modificados recentemente"""
        try:
            # Usar git se disponível
            if context.git_branch:
                result = subprocess.run(
                    ["git", "diff", "--name-only", "HEAD~5", "--", "*.py", "*.js", "*.ts", "*.go", "*.rs"],
                    cwd=self.path,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    context.recent_files = result.stdout.strip().split("\n")[:10]
                    return
            
            # Fallback: arquivos por data de modificação
            code_extensions = {".py", ".js", ".ts", ".go", ".rs", ".java", ".cs", ".rb", ".php"}
            files = []
            for f in self.path.rglob("*"):
                if f.is_file() and f.suffix in code_extensions:
                    if not any(p in str(f) for p in ["node_modules", "venv", ".git", "__pycache__", "dist", "build"]):
                        files.append((f, f.stat().st_mtime))
            
            files.sort(key=lambda x: x[1], reverse=True)
            context.recent_files = [str(f[0].relative_to(self.path)) for f in files[:10]]
            
        except Exception:
            pass
    
    def get_file_content(self, file_path: str, max_lines: int = 200) -> Optional[str]:
        """Lê conteúdo de um arquivo"""
        try:
            full_path = self.path / file_path
            if not full_path.exists():
                return None
            
            lines = full_path.read_text(encoding="utf-8").split("\n")
            if len(lines) > max_lines:
                return "\n".join(lines[:max_lines]) + f"\n\n... ({len(lines) - max_lines} linhas omitidas)"
            return "\n".join(lines)
        except Exception:
            return None
    
    def get_staged_diff(self) -> Optional[str]:
        """Obtém diff dos arquivos staged"""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached"],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout
        except Exception:
            pass
        return None


def detect_context(path: Optional[str] = None) -> ProjectContext:
    """Função de conveniência para detectar contexto"""
    return ContextDetector(path).detect()
