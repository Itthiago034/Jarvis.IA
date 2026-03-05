"""
JARVIS - Vision Tools
=====================
Ferramentas para análise visual usando Gemini.
Suporta screenshots, diagramas, wireframes, imagens de código.
"""

import os
import io
import base64
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

# Tentar importar bibliotecas opcionais
try:
    from PIL import Image, ImageGrab  # type: ignore[reportMissingImports]
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import google.genai as genai  # type: ignore[reportMissingImports]
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class VisionTools:
    """Ferramentas de visão computacional com Gemini"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self._client = None
        self._model = "gemini-2.5-flash"
        self._screenshots_dir = Path.home() / ".jarvis" / "screenshots"
        self._screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_client(self):
        """Obtém cliente do Gemini"""
        if not GENAI_AVAILABLE:
            raise ImportError("google-genai não está instalado")
        
        if self._client is None:
            self._client = genai.Client(api_key=self.api_key)
        return self._client
    
    def take_screenshot(self, region: Optional[tuple] = None) -> Path:
        """Captura screenshot da tela"""
        if not PIL_AVAILABLE:
            raise ImportError("Pillow não está instalado")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self._screenshots_dir / f"screenshot_{timestamp}.png"
        
        if region:
            screenshot = ImageGrab.grab(bbox=region)
        else:
            screenshot = ImageGrab.grab()
        
        screenshot.save(filepath)
        return filepath
    
    def image_to_base64(self, image_path: Union[str, Path]) -> str:
        """Converte imagem para base64"""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Imagem não encontrada: {path}")
        
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    async def analyze_image(self, image_path: Union[str, Path], prompt: str) -> str:
        """Analisa uma imagem com Gemini"""
        client = self._get_client()
        
        # Carregar imagem
        path = Path(image_path)
        if not path.exists():
            return f"Erro: Imagem não encontrada: {path}"
        
        # Determinar MIME type
        suffix = path.suffix.lower()
        mime_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".bmp": "image/bmp"
        }
        mime_type = mime_types.get(suffix, "image/png")
        
        # Ler imagem
        with open(path, "rb") as f:
            image_data = f.read()
        
        try:
            # Criar conteúdo multimodal
            response = await asyncio.to_thread(
                lambda: client.models.generate_content(
                    model=self._model,
                    contents=[
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": base64.b64encode(image_data).decode()
                            }
                        }
                    ]
                )
            )
            
            return response.text
            
        except Exception as e:
            return f"Erro na análise: {str(e)}"
    
    async def analyze_screenshot(self, prompt: str) -> str:
        """Captura e analisa screenshot da tela"""
        try:
            screenshot_path = self.take_screenshot()
            analysis = await self.analyze_image(screenshot_path, prompt)
            return f"📸 Screenshot salvo em: {screenshot_path}\n\n{analysis}"
        except Exception as e:
            return f"Erro ao analisar screenshot: {e}"
    
    async def compare_images(self, image1_path: str, image2_path: str, 
                            comparison_type: str = "visual") -> str:
        """Compara duas imagens"""
        client = self._get_client()
        
        path1 = Path(image1_path)
        path2 = Path(image2_path)
        
        if not path1.exists() or not path2.exists():
            return "Erro: Uma ou ambas as imagens não foram encontradas"
        
        prompts = {
            "visual": "Compare visualmente estas duas imagens. Descreva as diferenças e semelhanças.",
            "code": "Compare estes dois trechos de código/interface. Identifique mudanças, melhorias ou bugs.",
            "design": "Compare estes dois designs/mockups. Analise diferenças de layout, cores, UX.",
            "diff": "Identifique todas as diferenças entre estas duas imagens de forma detalhada."
        }
        
        prompt = prompts.get(comparison_type, prompts["visual"])
        
        # Carregar ambas as imagens
        with open(path1, "rb") as f:
            img1_data = base64.b64encode(f.read()).decode()
        with open(path2, "rb") as f:
            img2_data = base64.b64encode(f.read()).decode()
        
        try:
            response = await asyncio.to_thread(
                lambda: client.models.generate_content(
                    model=self._model,
                    contents=[
                        {"text": f"{prompt}\n\nImagem 1:"},
                        {"inline_data": {"mime_type": "image/png", "data": img1_data}},
                        {"text": "Imagem 2:"},
                        {"inline_data": {"mime_type": "image/png", "data": img2_data}}
                    ]
                )
            )
            
            return response.text
            
        except Exception as e:
            return f"Erro na comparação: {str(e)}"
    
    async def extract_text_from_image(self, image_path: str) -> str:
        """Extrai texto de uma imagem (OCR)"""
        prompt = """Extraia TODO o texto visível nesta imagem.
Mantenha a formatação original o máximo possível.
Se houver código, preserve a indentação.
Se houver tabelas, formate como tabela.
Não adicione interpretações, apenas extraia o texto literal."""
        
        return await self.analyze_image(image_path, prompt)
    
    async def analyze_diagram(self, image_path: str) -> str:
        """Analisa um diagrama técnico"""
        prompt = """Analise este diagrama técnico em detalhes:
1. Identifique o tipo de diagrama (UML, ER, Fluxo, Arquitetura, etc)
2. Descreva todos os componentes/entidades
3. Explique as relações/conexões entre eles
4. Identifique padrões de design, se houver
5. Sugira melhorias ou problemas potenciais

Seja técnico e preciso na análise."""
        
        return await self.analyze_image(image_path, prompt)
    
    async def analyze_ui_screenshot(self, image_path: str) -> str:
        """Analisa screenshot de interface/UI"""
        prompt = """Analise esta interface de usuário:
1. Descreva os elementos visuais (botões, forms, menus, etc)
2. Identifique problemas de UX/UI
3. Avalie acessibilidade (contraste, tamanhos, etc)
4. Sugira melhorias de design
5. Se houver erros visíveis, identifique-os

Forneça feedback construtivo e específico."""
        
        return await self.analyze_image(image_path, prompt)
    
    async def generate_code_from_image(self, image_path: str, 
                                       framework: str = "html") -> str:
        """Gera código a partir de uma imagem de design/wireframe"""
        frameworks = {
            "html": "HTML5 com CSS3 moderno (Flexbox/Grid), responsivo",
            "react": "React com componentes funcionais e Tailwind CSS",
            "vue": "Vue 3 com Composition API e CSS scoped",
            "flutter": "Flutter com widgets Material Design",
            "swift": "SwiftUI para iOS",
            "android": "Jetpack Compose para Android"
        }
        
        target = frameworks.get(framework.lower(), frameworks["html"])
        
        prompt = f"""Analise este design/wireframe e gere código funcional.

Framework/Tecnologia alvo: {target}

Requisitos:
1. Replique o layout o mais fielmente possível
2. Use componentes/elementos semânticos
3. Implemente responsividade
4. Adicione interações básicas onde apropriado
5. Comente partes complexas do código

Forneça o código completo e funcional."""
        
        return await self.analyze_image(image_path, prompt)
    
    async def debug_visual_bug(self, image_path: str, description: str = "") -> str:
        """Analisa screenshot para identificar bugs visuais"""
        prompt = f"""Analise esta imagem procurando por bugs visuais ou problemas.

{f"Descrição do problema reportado: {description}" if description else ""}

Identifique:
1. Elementos desalinhados ou sobrepostos
2. Problemas de cor/contraste
3. Texto truncado ou ilegível
4. Elementos faltando ou incorretos
5. Problemas de responsividade
6. Inconsistências visuais

Para cada problema encontrado, sugira a correção no código (CSS/HTML/etc)."""
        
        return await self.analyze_image(image_path, prompt)


# ==================== FUNÇÕES DE FERRAMENTA PARA O AGENTE ====================

def get_vision_tools():
    """Retorna as ferramentas de visão para o CodeAgent"""
    vision = VisionTools()
    
    async def screenshot_analyze(prompt: str = "Descreva o que você vê nesta tela") -> str:
        """
        Captura screenshot da tela e analisa com IA.
        
        Args:
            prompt: Pergunta ou instrução sobre a análise
        
        Returns:
            Análise da imagem
        """
        if not PIL_AVAILABLE:
            return "❌ Pillow não instalado. Execute: pip install Pillow"
        if not GENAI_AVAILABLE:
            return "❌ google-genai não instalado. Execute: pip install google-genai"
        
        return await vision.analyze_screenshot(prompt)
    
    async def analyze_image(image_path: str, prompt: str = "Descreva esta imagem") -> str:
        """
        Analisa uma imagem com IA.
        
        Args:
            image_path: Caminho para a imagem
            prompt: Pergunta ou instrução sobre a análise
        
        Returns:
            Análise da imagem
        """
        return await vision.analyze_image(image_path, prompt)
    
    async def extract_text(image_path: str) -> str:
        """
        Extrai texto de uma imagem (OCR).
        
        Args:
            image_path: Caminho para a imagem
        
        Returns:
            Texto extraído
        """
        return await vision.extract_text_from_image(image_path)
    
    async def analyze_diagram(image_path: str) -> str:
        """
        Analisa um diagrama técnico (UML, ER, Fluxo, etc).
        
        Args:
            image_path: Caminho para a imagem do diagrama
        
        Returns:
            Análise técnica do diagrama
        """
        return await vision.analyze_diagram(image_path)
    
    async def analyze_ui(image_path: str) -> str:
        """
        Analisa uma interface de usuário e sugere melhorias.
        
        Args:
            image_path: Caminho para screenshot da UI
        
        Returns:
            Análise de UX/UI com sugestões
        """
        return await vision.analyze_ui_screenshot(image_path)
    
    async def design_to_code(image_path: str, framework: str = "html") -> str:
        """
        Gera código a partir de um design/wireframe.
        
        Args:
            image_path: Caminho para imagem do design
            framework: Tecnologia alvo (html, react, vue, flutter, swift, android)
        
        Returns:
            Código gerado
        """
        return await vision.generate_code_from_image(image_path, framework)
    
    async def debug_visual(image_path: str, bug_description: str = "") -> str:
        """
        Analisa screenshot para encontrar bugs visuais.
        
        Args:
            image_path: Caminho para screenshot com o bug
            bug_description: Descrição opcional do problema
        
        Returns:
            Análise do bug com sugestões de correção
        """
        return await vision.debug_visual_bug(image_path, bug_description)
    
    async def compare_designs(image1: str, image2: str) -> str:
        """
        Compara dois designs ou screenshots.
        
        Args:
            image1: Caminho para primeira imagem
            image2: Caminho para segunda imagem
        
        Returns:
            Comparação detalhada
        """
        return await vision.compare_images(image1, image2, "design")
    
    return {
        "screenshot_analyze": screenshot_analyze,
        "analyze_image": analyze_image,
        "extract_text": extract_text,
        "analyze_diagram": analyze_diagram,
        "analyze_ui": analyze_ui,
        "design_to_code": design_to_code,
        "debug_visual": debug_visual,
        "compare_designs": compare_designs,
    }
