"""
JARVIS - Project Scaffolding Tools
==================================
Ferramentas para criar estruturas de projeto automaticamente.
Suporta Python, Node.js, React, FastAPI, Django, etc.
"""

import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProjectScaffolder:
    """Gerador de estruturas de projeto"""
    
    # Templates de projeto
    TEMPLATES = {
        "python-basic": {
            "description": "Projeto Python básico com estrutura padrão",
            "files": {
                "src/__init__.py": "",
                "src/main.py": '''"""Módulo principal."""

def main():
    """Função principal."""
    print("Hello, World!")

if __name__ == "__main__":
    main()
''',
                "tests/__init__.py": "",
                "tests/test_main.py": '''"""Testes do módulo principal."""
import pytest
from src.main import main

def test_main():
    """Testa a função main."""
    # TODO: Implementar teste
    assert True
''',
                "requirements.txt": "pytest>=8.0.0\nruff>=0.3.0\n",
                ".gitignore": "__pycache__/\n*.pyc\n.env\nvenv/\n.pytest_cache/\ndist/\n*.egg-info/\n",
                "README.md": "# {project_name}\n\n{description}\n\n## Instalação\n\n```bash\npip install -r requirements.txt\n```\n\n## Uso\n\n```bash\npython src/main.py\n```\n",
                "pyproject.toml": '''[project]
name = "{project_name}"
version = "0.1.0"
description = "{description}"
requires-python = ">=3.10"

[tool.ruff]
line-length = 100
''',
            }
        },
        
        "fastapi": {
            "description": "API REST com FastAPI",
            "files": {
                "app/__init__.py": "",
                "app/main.py": '''"""FastAPI Application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="{project_name}",
    description="{description}",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Welcome to {project_name}"}

@app.get("/api/v1/health")
async def health():
    """API health check."""
    return {"status": "healthy"}
''',
                "app/config.py": '''"""Application configuration."""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    app_name: str = "{project_name}"
    debug: bool = False
    database_url: str = "sqlite:///./app.db"
    
    class Config:
        env_file = ".env"

settings = Settings()
''',
                "app/routers/__init__.py": "",
                "app/routers/items.py": '''"""Items router."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/v1/items", tags=["items"])

class Item(BaseModel):
    id: int
    name: str
    description: str | None = None

# In-memory storage (replace with database)
items_db: List[Item] = []

@router.get("/", response_model=List[Item])
async def list_items():
    """List all items."""
    return items_db

@router.post("/", response_model=Item)
async def create_item(item: Item):
    """Create a new item."""
    items_db.append(item)
    return item

@router.get("/{item_id}", response_model=Item)
async def get_item(item_id: int):
    """Get item by ID."""
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")
''',
                "app/models/__init__.py": "",
                "tests/__init__.py": "",
                "tests/test_api.py": '''"""API tests."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
''',
                "requirements.txt": "fastapi>=0.109.0\nuvicorn[standard]>=0.27.0\npydantic>=2.5.0\npydantic-settings>=2.1.0\npytest>=8.0.0\nhttpx>=0.26.0\n",
                ".env.example": "DEBUG=false\nDATABASE_URL=sqlite:///./app.db\n",
                ".gitignore": "__pycache__/\n*.pyc\n.env\nvenv/\n.pytest_cache/\n*.db\n",
                "README.md": '''# {project_name}

{description}

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload

# Run tests
pytest
```

## API Documentation

After starting the server, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
''',
                "Dockerfile": '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
''',
            }
        },
        
        "react": {
            "description": "Aplicação React com Vite e TypeScript",
            "files": {
                "src/main.tsx": '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
''',
                "src/App.tsx": '''import { useState } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="App">
      <h1>{project_name}</h1>
      <p>{description}</p>
      <button onClick={() => setCount(c => c + 1)}>
        Count: {count}
      </button>
    </div>
  )
}

export default App
''',
                "src/App.css": '''.App {
  text-align: center;
  padding: 2rem;
}

button {
  padding: 0.5rem 1rem;
  font-size: 1rem;
  cursor: pointer;
}
''',
                "src/index.css": '''* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
''',
                "index.html": '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
''',
                "package.json": '''{
  "name": "{project_name_slug}",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext ts,tsx"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "eslint": "^8.56.0"
  }
}
''',
                "tsconfig.json": '''{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
''',
                "vite.config.ts": '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
''',
                ".gitignore": "node_modules/\ndist/\n.env\n*.local\n",
                "README.md": '''# {project_name}

{description}

## Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build
```
''',
            }
        },
        
        "node-api": {
            "description": "API Node.js com Express e TypeScript",
            "files": {
                "src/index.ts": '''import express from 'express';
import cors from 'cors';
import { router } from './routes';

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.use('/api', router);

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
''',
                "src/routes/index.ts": '''import { Router } from 'express';

export const router = Router();

router.get('/items', (req, res) => {
  res.json({ items: [] });
});

router.post('/items', (req, res) => {
  const { name } = req.body;
  res.json({ id: Date.now(), name });
});
''',
                "package.json": '''{
  "name": "{project_name_slug}",
  "version": "0.1.0",
  "scripts": {
    "dev": "ts-node-dev --respawn src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js"
  },
  "dependencies": {
    "express": "^4.18.0",
    "cors": "^2.8.5"
  },
  "devDependencies": {
    "@types/express": "^4.17.0",
    "@types/cors": "^2.8.0",
    "@types/node": "^20.0.0",
    "typescript": "^5.3.0",
    "ts-node-dev": "^2.0.0"
  }
}
''',
                "tsconfig.json": '''{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*"]
}
''',
                ".gitignore": "node_modules/\ndist/\n.env\n",
                "README.md": '''# {project_name}

{description}

## Development

```bash
npm install
npm run dev
```
''',
            }
        },
        
        "django": {
            "description": "Aplicação Django com estrutura padrão",
            "files": {
                "manage.py": '''#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project_name_slug}.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
''',
                "{project_name_slug}/__init__.py": "",
                "{project_name_slug}/settings.py": '''from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'change-me-in-production'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = '{project_name_slug}.urls'
WSGI_APPLICATION = '{project_name_slug}.wsgi.application'

DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }}
}}

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
''',
                "{project_name_slug}/urls.py": '''from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]
''',
                "{project_name_slug}/wsgi.py": '''import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project_name_slug}.settings')
application = get_wsgi_application()
''',
                "requirements.txt": "Django>=5.0\n",
                ".gitignore": "__pycache__/\n*.pyc\n.env\ndb.sqlite3\n",
                "README.md": '''# {project_name}

{description}

## Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
''',
            }
        },
    }
    
    @classmethod
    def list_templates(cls) -> Dict[str, str]:
        """Lista templates disponíveis"""
        return {name: t["description"] for name, t in cls.TEMPLATES.items()}
    
    @classmethod
    def create_project(cls, template: str, project_name: str,
                       output_dir: str, description: str = "") -> Dict[str, Any]:
        """Cria projeto a partir de um template"""
        if template not in cls.TEMPLATES:
            return {"success": False, "error": f"Template '{template}' não encontrado"}
        
        tmpl = cls.TEMPLATES[template]
        project_path = Path(output_dir) / project_name
        
        if project_path.exists():
            return {"success": False, "error": f"Diretório já existe: {project_path}"}
        
        # Criar diretório principal
        project_path.mkdir(parents=True)
        
        # Substituições
        project_name_slug = project_name.lower().replace(" ", "_").replace("-", "_")
        replacements = {
            "{project_name}": project_name,
            "{project_name_slug}": project_name_slug,
            "{description}": description or f"Projeto {project_name}",
        }
        
        created_files = []
        
        for filepath, content in tmpl["files"].items():
            # Aplicar substituições no path
            for old, new in replacements.items():
                filepath = filepath.replace(old, new)
            
            # Aplicar substituições no conteúdo
            for old, new in replacements.items():
                content = content.replace(old, new)
            
            # Criar arquivo
            file_path = project_path / filepath
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            created_files.append(filepath)
        
        return {
            "success": True,
            "path": str(project_path),
            "template": template,
            "files": created_files
        }


# ==================== FUNÇÕES DE FERRAMENTA PARA O AGENTE ====================

def get_scaffolding_tools():
    """Retorna as ferramentas de scaffolding para o CodeAgent"""
    scaffolder = ProjectScaffolder()
    
    def list_project_templates() -> str:
        """
        Lista todos os templates de projeto disponíveis.
        
        Returns:
            Lista de templates com descrições
        """
        templates = scaffolder.list_templates()
        
        output = ["📁 **Templates de Projeto Disponíveis:**\n"]
        for name, desc in templates.items():
            output.append(f"  • **{name}**: {desc}")
        
        output.append("\n\nUse `create_project` para criar um projeto.")
        return "\n".join(output)
    
    def create_project(template: str, name: str, output_dir: str = ".",
                       description: str = "") -> str:
        """
        Cria um novo projeto a partir de um template.
        
        Args:
            template: Nome do template (python-basic, fastapi, react, node-api, django)
            name: Nome do projeto
            output_dir: Diretório onde criar (padrão: atual)
            description: Descrição do projeto
        
        Returns:
            Status da criação
        """
        result = scaffolder.create_project(template, name, output_dir, description)
        
        if not result["success"]:
            return f"❌ Erro: {result['error']}"
        
        output = [
            f"✅ Projeto **{name}** criado com sucesso!",
            f"📁 Local: `{result['path']}`",
            f"📋 Template: {result['template']}",
            f"\n📄 Arquivos criados ({len(result['files'])}):"
        ]
        
        for f in result['files'][:15]:
            output.append(f"  • {f}")
        
        if len(result['files']) > 15:
            output.append(f"  ... e mais {len(result['files']) - 15} arquivos")
        
        # Instruções de próximos passos
        if template == "fastapi":
            output.extend([
                "\n🚀 **Próximos passos:**",
                "```bash",
                f"cd {name}",
                "pip install -r requirements.txt",
                "uvicorn app.main:app --reload",
                "```"
            ])
        elif template == "react":
            output.extend([
                "\n🚀 **Próximos passos:**",
                "```bash",
                f"cd {name}",
                "npm install",
                "npm run dev",
                "```"
            ])
        elif template in ["python-basic", "django"]:
            output.extend([
                "\n🚀 **Próximos passos:**",
                "```bash",
                f"cd {name}",
                "pip install -r requirements.txt",
                "```"
            ])
        elif template == "node-api":
            output.extend([
                "\n🚀 **Próximos passos:**",
                "```bash",
                f"cd {name}",
                "npm install",
                "npm run dev",
                "```"
            ])
        
        return "\n".join(output)
    
    def add_file_to_project(project_dir: str, filepath: str, content: str) -> str:
        """
        Adiciona um arquivo a um projeto existente.
        
        Args:
            project_dir: Diretório do projeto
            filepath: Caminho do arquivo (relativo ao projeto)
            content: Conteúdo do arquivo
        
        Returns:
            Confirmação
        """
        project_path = Path(project_dir)
        if not project_path.exists():
            return f"❌ Projeto não encontrado: {project_dir}"
        
        file_path = project_path / filepath
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        
        return f"✅ Arquivo criado: {filepath}"
    
    return {
        "list_project_templates": list_project_templates,
        "create_project": create_project,
        "add_file_to_project": add_file_to_project,
    }
