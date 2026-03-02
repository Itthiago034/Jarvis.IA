# 🔧 Funcionalidades do LLM Agent para Integrar no JARVIS

> Auditoria realizada em: 1 de março de 2026  
> Fonte: `C:\Users\Thiago\OneDrive\Documentos\LLM Agent`

---

## 📋 Resumo Executivo

O projeto **LLM Agent** contém implementações prontas de funcionalidades avançadas que podem transformar o JARVIS em um assistente muito mais poderoso. As principais oportunidades são:

| Prioridade | Funcionalidade | Impacto |
|------------|----------------|---------|
| 🔴 Alta | Sistema RAG | JARVIS aprende sua documentação |
| 🔴 Alta | Busca no código (grep) | Encontra funções/classes no projeto |
| 🟡 Média | Edição de arquivos | Edita trechos sem reescrever tudo |
| 🟡 Média | Executor Python | Roda snippets de código |
| 🟢 Baixa | APIs alternativas | Fallback gratuito (Groq, Ollama) |

---

## 1. 🔍 Sistema RAG (Retrieval-Augmented Generation)

**Arquivo fonte:** `04_rag_sistema.py`

### O que faz:
Permite que o JARVIS responda perguntas baseado em **sua própria documentação, código ou arquivos**. Ele indexa documentos em um banco vetorial e busca informações relevantes antes de responder.

### Casos de uso:
- "JARVIS, como funciona a função X no meu projeto?"
- "O que diz a documentação sobre autenticação?"
- "Procure nos meus arquivos como configurar o Docker"

### Código adaptável:

```python
# Dependências necessárias
# pip install langchain langchain-community chromadb sentence-transformers

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from pathlib import Path
from typing import List, Dict
import os

CONFIG_RAG = {
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "persist_directory": "./jarvis_knowledge",
    "chunk_size": 500,
    "chunk_overlap": 50,
    "top_k": 4,
}

class JarvisRAG:
    """Sistema RAG para o JARVIS aprender sua documentação"""
    
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=CONFIG_RAG["embedding_model"],
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self.vectorstore = None
    
    def indexar_diretorio(self, diretorio: str, extensoes: List[str] = None):
        """Indexa todos os arquivos de um diretório"""
        extensoes = extensoes or ['.py', '.md', '.txt', '.js', '.html']
        documentos = []
        
        for arquivo in Path(diretorio).rglob('*'):
            if arquivo.is_file() and arquivo.suffix.lower() in extensoes:
                try:
                    content = arquivo.read_text(encoding='utf-8')
                    documentos.append(Document(
                        page_content=content,
                        metadata={"source": str(arquivo)}
                    ))
                except:
                    pass
        
        # Divide em chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CONFIG_RAG["chunk_size"],
            chunk_overlap=CONFIG_RAG["chunk_overlap"]
        )
        
        chunks = text_splitter.split_documents(documentos)
        
        # Cria vector store
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=CONFIG_RAG["persist_directory"]
        )
        self.vectorstore.persist()
        
        return f"Indexados {len(chunks)} chunks de {len(documentos)} arquivos"
    
    def buscar(self, query: str, k: int = 4) -> List[Dict]:
        """Busca documentos relevantes"""
        if not self.vectorstore:
            self.vectorstore = Chroma(
                persist_directory=CONFIG_RAG["persist_directory"],
                embedding_function=self.embeddings
            )
        
        docs = self.vectorstore.similarity_search(query, k=k)
        return [{"content": doc.page_content, "source": doc.metadata.get("source")} for doc in docs]
```

### Integração no JARVIS:

```python
@function_tool(
    name="buscar_conhecimento",
    description="Busca informações na base de conhecimento do JARVIS (documentação, código, arquivos indexados)"
)
async def buscar_conhecimento(self, pergunta: str) -> str:
    rag = JarvisRAG()
    resultados = rag.buscar(pergunta)
    if resultados:
        return "\n\n".join([f"[{r['source']}]\n{r['content']}" for r in resultados])
    return "Não encontrei informações relevantes."
```

---

## 2. 🔎 Busca no Código (Grep Search)

**Arquivo fonte:** `agente_ollama.py`

### O que faz:
Busca padrões (texto ou regex) em arquivos do projeto. Essencial para encontrar funções, classes, variáveis.

### Casos de uso:
- "JARVIS, onde está definida a função login?"
- "Procure por TODO no código"
- "Encontre todas as classes que herdam de Agent"

### Código adaptável:

```python
import re
from pathlib import Path
from typing import List

def grep_search(
    pattern: str, 
    directory: str = ".", 
    extensions: List[str] = None,
    max_results: int = 20
) -> dict:
    """
    Busca padrão em arquivos do projeto
    
    Args:
        pattern: Texto ou regex a buscar
        directory: Diretório raiz da busca
        extensions: Extensões de arquivo (.py, .js, etc)
        max_results: Máximo de resultados
    
    Returns:
        Dict com resultados ou erro
    """
    extensions = extensions or ['.py', '.js', '.ts', '.json', '.md', '.txt', '.html', '.css']
    results = []
    
    try:
        path = Path(directory)
        
        for file_path in path.rglob('*'):
            if file_path.is_file() and file_path.suffix in extensions:
                try:
                    content = file_path.read_text(encoding='utf-8')
                    for i, line in enumerate(content.split('\n'), 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            results.append({
                                "file": str(file_path),
                                "line": i,
                                "content": line.strip()[:200]
                            })
                            
                            if len(results) >= max_results:
                                break
                except:
                    pass
            
            if len(results) >= max_results:
                break
        
        return {
            "success": True,
            "count": len(results),
            "results": results
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### Integração no JARVIS:

```python
@function_tool(
    name="buscar_no_codigo",
    description="Busca um padrão (texto ou regex) em arquivos de código do projeto. Use para encontrar funções, classes, variáveis."
)
async def buscar_no_codigo(self, padrao: str, diretorio: str = ".") -> str:
    resultado = grep_search(padrao, diretorio)
    
    if not resultado["success"]:
        return f"Erro na busca: {resultado['error']}"
    
    if resultado["count"] == 0:
        return f"Nenhum resultado para '{padrao}'"
    
    output = f"Encontrados {resultado['count']} resultados:\n\n"
    for r in resultado["results"]:
        output += f"📄 {r['file']}:{r['line']}\n   {r['content']}\n\n"
    
    return output
```

---

## 3. ✏️ Edição de Arquivos (Replace)

**Arquivo fonte:** `agente_ollama.py`

### O que faz:
Edita trechos específicos de arquivos sem precisar reescrever o arquivo inteiro. Mais seguro e preciso.

### Casos de uso:
- "JARVIS, substitua 'print' por 'logger.info' no arquivo X"
- "Corrija o bug na linha 42"
- "Adicione um comentário antes da função main"

### Código adaptável:

```python
def editar_arquivo(caminho: str, texto_antigo: str, texto_novo: str) -> dict:
    """
    Substitui texto em um arquivo existente
    
    Args:
        caminho: Caminho do arquivo
        texto_antigo: Texto a ser substituído
        texto_novo: Novo texto
    
    Returns:
        Dict com sucesso ou erro
    """
    try:
        path = Path(caminho)
        
        if not path.exists():
            return {"success": False, "error": f"Arquivo não encontrado: {caminho}"}
        
        content = path.read_text(encoding='utf-8')
        
        if texto_antigo not in content:
            return {"success": False, "error": "Texto não encontrado no arquivo"}
        
        # Conta ocorrências
        count = content.count(texto_antigo)
        
        # Substitui (apenas primeira ocorrência por segurança)
        new_content = content.replace(texto_antigo, texto_novo, 1)
        path.write_text(new_content, encoding='utf-8')
        
        return {
            "success": True,
            "message": f"Substituição realizada ({count} ocorrência(s) encontrada(s))"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### Integração no JARVIS:

```python
@function_tool(
    name="editar_arquivo",
    description="Edita um arquivo substituindo um trecho de texto por outro. Útil para correções pontuais sem reescrever o arquivo inteiro."
)
async def editar_arquivo_tool(self, caminho: str, texto_antigo: str, texto_novo: str) -> str:
    resultado = editar_arquivo(caminho, texto_antigo, texto_novo)
    
    if resultado["success"]:
        return f"✅ {resultado['message']}"
    else:
        return f"❌ {resultado['error']}"
```

---

## 4. 🐍 Executor de Python

**Arquivo fonte:** `05_agente_codigo.py`

### O que faz:
Executa código Python e retorna o resultado. Útil para cálculos, testes rápidos, manipulação de dados.

### Casos de uso:
- "JARVIS, calcule a soma de 1 a 100"
- "Execute esse snippet e me diga o resultado"
- "Teste se essa regex funciona"

### Código adaptável:

```python
import io
import sys
from contextlib import redirect_stdout, redirect_stderr

def executar_python(code: str, timeout: int = 10) -> dict:
    """
    Executa código Python de forma segura
    
    Args:
        code: Código Python a executar
        timeout: Tempo máximo (não implementado - requer threading)
    
    Returns:
        Dict com output, errors, success
    
    ⚠️ SEGURANÇA: Em produção, use sandboxing adequado!
    """
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    
    # Ambiente de execução limitado
    exec_globals = {
        '__builtins__': {
            'print': print,
            'range': range,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'list': list,
            'dict': dict,
            'sum': sum,
            'max': max,
            'min': min,
            'sorted': sorted,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'abs': abs,
            'round': round,
            'type': type,
            'isinstance': isinstance,
            'True': True,
            'False': False,
            'None': None,
        }
    }
    
    try:
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            exec(code, exec_globals)
        
        output = stdout_buffer.getvalue()
        errors = stderr_buffer.getvalue()
        
        return {
            "success": True,
            "output": output or "(sem output)",
            "errors": errors
        }
        
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "errors": f"{type(e).__name__}: {str(e)}"
        }
```

### Integração no JARVIS:

```python
@function_tool(
    name="executar_python",
    description="Executa um snippet de código Python e retorna o resultado. Útil para cálculos, testes rápidos e manipulação de dados."
)
async def executar_python_tool(self, codigo: str) -> str:
    resultado = executar_python(codigo)
    
    response = ""
    if resultado["output"]:
        response += f"📤 Output:\n{resultado['output']}\n"
    if resultado["errors"]:
        response += f"❌ Erros:\n{resultado['errors']}"
    
    if not response:
        response = "✅ Código executado sem output"
    
    return response
```

---

## 5. 🌐 APIs de LLM Alternativas (Fallback)

**Arquivo fonte:** `06_usando_apis_llm.py`

### O que faz:
Permite usar diferentes provedores de LLM como fallback ou alternativa. Útil quando a API principal falha ou para reduzir custos.

### Provedores disponíveis:

| Provider | Custo | Velocidade | Como usar |
|----------|-------|------------|-----------|
| **Groq** | Grátis! | Muito rápida | `GROQ_API_KEY` |
| **Ollama** | Grátis (local) | Depende do PC | `ollama serve` |
| **Google Gemini** | Grátis (limites) | Rápida | `GOOGLE_API_KEY` |
| **OpenAI** | Pago | Rápida | `OPENAI_API_KEY` |

### Código para Groq (recomendado como fallback):

```python
# pip install groq

from groq import Groq
import os

def chamar_groq(prompt: str, system_prompt: str = None) -> str:
    """
    Usa Groq como LLM - GRATUITO e muito rápido!
    
    API Key grátis: https://console.groq.com/keys
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Configure GROQ_API_KEY"
    
    client = Groq(api_key=api_key)
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # Rápido e gratuito
        messages=messages,
        temperature=0.7,
        max_tokens=1000,
    )
    
    return response.choices[0].message.content
```

### Código para Ollama (100% local):

```python
import requests

def chamar_ollama(prompt: str, model: str = "llama3:8b") -> str:
    """
    Usa Ollama - roda LLMs LOCALMENTE no PC
    
    Instalação: https://ollama.com/download
    Depois: ollama pull llama3:8b
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()["message"]["content"]
        return f"Erro: {response.status_code}"
        
    except requests.exceptions.ConnectionError:
        return "Ollama não está rodando. Execute: ollama serve"
```

---

## 📁 Estrutura Final Sugerida

```
Jarvis.IA/
├── agent.py              # Agente principal (já existe)
├── prompts.py            # Instruções do agente (já existe)
├── wsl_tools.py          # Comandos WSL (já existe)
├── windows_tools.py      # Comandos Windows (já existe)
├── file_tools.py         # Ler/escrever arquivos (já existe)
├── grep_tools.py         # 🆕 Busca no código
├── python_executor.py    # 🆕 Executor Python
├── rag_tools.py          # 🆕 Sistema RAG
├── llm_fallback.py       # 🆕 APIs alternativas
└── jarvis_knowledge/     # 🆕 Base de conhecimento RAG
```

---

## 🚀 Ordem de Implementação Recomendada

1. **grep_tools.py** - Implementação simples, alto impacto
2. **python_executor.py** - Útil para cálculos e testes
3. **rag_tools.py** - Mais complexo, mas transforma o JARVIS
4. **llm_fallback.py** - Opcional, bom ter como backup

---

## 📦 Dependências Adicionais

```txt
# Para RAG
langchain>=0.1.0
langchain-community>=0.0.10
chromadb>=0.4.0
sentence-transformers>=2.2.0

# Para APIs alternativas
groq>=0.4.0
google-generativeai>=0.3.0
```

---

## ✅ Checklist de Implementação

- [ ] Criar `grep_tools.py`
- [ ] Criar `python_executor.py`
- [ ] Criar `rag_tools.py`
- [ ] Criar `llm_fallback.py`
- [ ] Adicionar function_tools no `agent.py`
- [ ] Atualizar `prompts.py` com novas capacidades
- [ ] Atualizar `requirements.txt`
- [ ] Testar todas as ferramentas
- [ ] Indexar documentação no RAG

---

*Documento gerado automaticamente. Consulte os arquivos originais em `C:\Users\Thiago\OneDrive\Documentos\LLM Agent` para mais detalhes.*
