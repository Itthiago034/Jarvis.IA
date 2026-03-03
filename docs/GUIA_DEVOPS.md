# Guia DevOps - Ferramentas de Suporte ao Desenvolvimento

Este guia explica as ferramentas sugeridas no relatório de arquitetura e **por que elas NÃO afetam o funcionamento do Jarvis**.

---

## ⚠️ Importante: Isso Afeta o Jarvis?

| Ferramenta | Afeta o funcionamento? | Explicação |
|------------|------------------------|------------|
| `.gitignore` | ❌ NÃO | Apenas controla o que vai para o GitHub |
| `GitHub Actions` | ❌ NÃO | Roda apenas no GitHub, não no seu PC |
| `Ruff/Black` | ❌ NÃO | Apenas formata código, não muda lógica |
| `pytest` | ❌ NÃO | Apenas testa, não altera nada |

**Resumo:** Todas essas ferramentas são "auxiliares de bastidores". O Jarvis continuará funcionando exatamente da mesma forma.

---

## 1. O que é `.gitignore`?

### Função
O `.gitignore` é um arquivo de texto que diz ao Git: **"ignore esses arquivos, não envie para o GitHub"**.

### Por que usar?
Sem ele, você corre riscos como:

| Risco | Consequência |
|-------|--------------|
| Enviar `.env` com suas API keys | Qualquer pessoa pode ver suas credenciais |
| Enviar pasta `venv/` | Repositório fica gigante (centenas de MB) |
| Enviar `__pycache__/` | Lixo desnecessário no GitHub |

### Como funciona?

```
# Exemplo de .gitignore

# Ignora a pasta venv
venv/

# Ignora arquivos .env (suas senhas!)
.env

# Ignora cache do Python
__pycache__/
*.pyc
```

### Analogia simples
Pense assim: você está enviando uma mala de viagem (seu código) para um amigo (GitHub).

- **Sem `.gitignore`**: Você manda TUDO - roupas, lixo, carregadores, até a escova de dente usada
- **Com `.gitignore`**: Você manda só o necessário - roupas limpas e organizadas

### O que acontece quando você cria um `.gitignore`?

**Antes:**
```
git status
→ Mostra: venv/ (5000 arquivos), .env, __pycache__/, agent.py, prompts.py...
```

**Depois:**
```
git status
→ Mostra: agent.py, prompts.py (apenas seus arquivos de código)
```

### Isso muda o Jarvis?
**NÃO.** O `.gitignore` só afeta o que vai para o GitHub. Seus arquivos locais continuam existindo e funcionando normalmente.

---

## 2. O que é GitHub Actions?

### Função
GitHub Actions é um **robô automático** que roda no servidor do GitHub toda vez que você faz um `push`.

### Arquivo `.github/workflows/ci.yml`

```yaml
name: CI                          # Nome do workflow

on:                               # Quando executar?
  push:                           # Quando alguém faz push...
    branches: [main]              # ...na branch main
  pull_request:                   # OU quando alguém abre um PR
    branches: [main]

jobs:                             # O que fazer?
  lint:                           # Job 1: Verificar qualidade do código
    runs-on: ubuntu-latest        # Usa uma máquina Linux do GitHub
    steps:
      - uses: actions/checkout@v4 # Baixa seu código
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'  # Instala Python
      - name: Install dependencies
        run: pip install ruff     # Instala o linter
      - name: Run Ruff
        run: ruff check .         # Verifica erros de código

  test:                           # Job 2: Rodar testes
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: pytest tests/ -v     # Executa os testes
```

### Analogia simples
Imagine que você contratou um **estagiário robô** que:
1. Fica esperando você fazer push
2. Quando você faz, ele baixa seu código
3. Verifica se tem erros
4. Te avisa se algo está errado

Você não precisa fazer nada - ele trabalha sozinho no GitHub.

### O que cada parte faz?

| Seção | Significado |
|-------|-------------|
| `on: push` | "Execute quando alguém fizer push" |
| `branches: [main]` | "Apenas na branch main" |
| `runs-on: ubuntu-latest` | "Use um servidor Linux do GitHub" |
| `steps` | Lista de comandos a executar |
| `uses: actions/checkout@v4` | "Baixe o código do repositório" |
| `run: ruff check .` | "Execute este comando" |

### Onde isso roda?
**NO GITHUB.** Não no seu computador.

```
┌─────────────────────┐         ┌─────────────────────┐
│   SEU COMPUTADOR    │         │      GITHUB         │
│                     │         │                     │
│  1. Você faz push ──┼────────►│  2. GitHub Actions  │
│                     │         │     roda o CI       │
│                     │         │                     │
│  4. Você vê o      │◄────────┼── 3. Resultado:     │
│     resultado       │         │     ✅ ou ❌        │
└─────────────────────┘         └─────────────────────┘
```

### Isso muda o Jarvis?
**NÃO.** O GitHub Actions roda em servidores do GitHub, não no seu PC. Seu Jarvis local continua funcionando normalmente.

---

## 3. Benefícios Práticos

### Cenário SEM essas ferramentas:

```
1. Você faz uma alteração no código
2. Faz commit e push
3. Acidentalmente envia o .env com suas API keys
4. Alguém vê suas keys e usa sua conta
5. Você recebe uma conta de $500 da OpenAI/Google
```

### Cenário COM essas ferramentas:

```
1. Você faz uma alteração no código
2. .gitignore bloqueia o .env automaticamente
3. Faz commit e push (sem o .env!)
4. GitHub Actions verifica se o código está ok
5. Você recebe um ✅ verde no GitHub
6. Suas keys estão seguras
```

---

## 4. Passo a Passo para Implementar

### Passo 1: Criar o `.gitignore`
Crie um arquivo chamado `.gitignore` na raiz do `Jarvis.IA/`:

```gitignore
# Ambiente virtual
venv/
.venv/

# Variáveis de ambiente (SUAS SENHAS!)
.env
.env.local
.env.*.local

# Cache do Python
__pycache__/
*.py[cod]
*$py.class
*.so

# Logs
*.log
logs/
KMS/logs/*
KMS/screenshots/*

# IDE
.vscode/
.idea/
*.swp
*.swo

# Sistema
.DS_Store
Thumbs.db
desktop.ini

# Temporários
*.tmp
*.temp
```

### Passo 2: Criar pasta do GitHub Actions (opcional)
```
Jarvis.IA/
└── .github/
    └── workflows/
        └── ci.yml
```

### Passo 3: Criar `.env.example`
Um template para outras pessoas saberem quais variáveis precisam:

```env
# Copie este arquivo para .env e preencha com suas chaves
GOOGLE_API_KEY=sua_chave_aqui
MEM0_API_KEY=sua_chave_aqui
LIVEKIT_URL=sua_url_aqui
LIVEKIT_API_KEY=sua_chave_aqui
LIVEKIT_API_SECRET=seu_secret_aqui
```

---

## 5. Resumo Visual

```
┌────────────────────────────────────────────────────────────────┐
│                    FERRAMENTAS DEVOPS                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│   .gitignore          GitHub Actions         pytest            │
│   ┌─────────┐         ┌─────────────┐       ┌─────────┐       │
│   │ Protege │         │ Verifica    │       │ Testa   │       │
│   │ seus    │         │ código      │       │ código  │       │
│   │ secrets │         │ no GitHub   │       │ local   │       │
│   └─────────┘         └─────────────┘       └─────────┘       │
│        │                    │                    │             │
│        ▼                    ▼                    ▼             │
│   Não envia           Roda no          Garante que            │
│   .env para           servidor         tudo funciona          │
│   o GitHub            do GitHub        antes de usar          │
│                                                                │
│   ════════════════════════════════════════════════════════    │
│                                                                │
│        NENHUM DELES ALTERA O FUNCIONAMENTO DO JARVIS!         │
│                                                                │
│   O Jarvis continua:                                          │
│   ✅ Ouvindo sua voz                                          │
│   ✅ Respondendo como antes                                   │
│   ✅ Salvando memórias                                        │
│   ✅ Executando automações                                    │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 6. FAQ

### "Se eu criar o .gitignore, vou perder meu .env?"
**NÃO.** O arquivo continua no seu PC. Ele só não vai para o GitHub.

### "O GitHub Actions pode quebrar meu código?"
**NÃO.** Ele apenas LEIA e verifica. Não modifica nada.

### "Preciso pagar pelo GitHub Actions?"
**NÃO** para repositórios públicos. Repositórios privados têm 2000 minutos/mês grátis.

### "Posso usar o Jarvis sem nada disso?"
**SIM.** Tudo isso é opcional. São boas práticas, não requisitos.

### "O que acontece se eu não usar?"
Funciona igual, mas:
- Risco de vazar suas API keys
- Repositório mais pesado
- Sem verificação automática de erros

---

## 7. Conclusão

| Ferramenta | O que faz | Afeta o Jarvis? |
|------------|-----------|-----------------|
| `.gitignore` | Protege seus secrets | ❌ NÃO |
| `GitHub Actions` | Verifica código automaticamente | ❌ NÃO |
| `Ruff/Black` | Formata código bonito | ❌ NÃO |
| `pytest` | Testa se tudo funciona | ❌ NÃO |

**Essas ferramentas são como um cinto de segurança:** não mudam como você dirige, mas te protegem em caso de acidente.

O Jarvis continuará funcionando **exatamente igual**. Essas ferramentas apenas tornam o desenvolvimento mais seguro e organizado.

---

*Documento criado para esclarecer dúvidas sobre DevOps e boas práticas de desenvolvimento.*
