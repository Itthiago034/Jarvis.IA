# Guia de Erros Comuns e Soluções

Este guia documenta erros comuns encontrados durante o desenvolvimento do projeto JARVIS e como resolvê-los.

---

## Índice

1. [Erro ao Ativar o Virtual Environment](#1-erro-ao-ativar-o-virtual-environment)
2. [Erro de Política de Execução do PowerShell](#2-erro-de-política-de-execução-do-powershell)
3. [Erro de API Key Expirada](#3-erro-de-api-key-expirada)
4. [Conceitos Importantes](#4-conceitos-importantes)

---

## 1. Erro ao Ativar o Virtual Environment

### O Erro
```
.\venv\Script\activate : O termo '.\venv\Script\activate' não é reconhecido como nome de cmdlet, 
função, arquivo de script ou programa operável.
```

### Causa
Erro de digitação! O nome da pasta é **Scripts** (com **S** no final), não "Script".

### Solução
Use o comando correto:
```powershell
# ❌ ERRADO
.\venv\Script\activate

# ✅ CORRETO
.\venv\Scripts\activate
```

### Dica
Você pode usar a tecla **Tab** para autocompletar:
1. Digite `.\venv\Scr`
2. Pressione **Tab**
3. O PowerShell completa para `.\venv\Scripts\`

---

## 2. Erro de Política de Execução do PowerShell

### O Erro
```
.\venv\Scripts\activate : O arquivo não pode ser carregado porque a execução de scripts foi 
desabilitada neste sistema.
```

### Causa
O Windows bloqueia a execução de scripts por segurança por padrão.

### Solução

**Passo 1:** Abra o PowerShell como **Administrador**
- Clique com botão direito no menu Iniciar
- Selecione "Windows PowerShell (Admin)" ou "Terminal (Admin)"

**Passo 2:** Execute o comando:
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Passo 3:** Quando perguntar, digite `S` ou `A` e pressione Enter:
```
[S] Sim  [A] Sim para Todos  [N] Não  ...
```

**Passo 4:** Feche o PowerShell de Admin e volte ao terminal do VS Code

### O que esse comando faz?
| Política | Significado |
|----------|-------------|
| `RemoteSigned` | Permite scripts locais, mas exige assinatura para scripts baixados da internet |
| `-Scope CurrentUser` | Aplica apenas para seu usuário, não para todo o sistema |

### Verificar a política atual
```powershell
Get-ExecutionPolicy -List
```

---

## 3. Erro de API Key Expirada

### O Erro
```
google.genai.errors.APIError: 1007 None. API key expired. Please renew the API key.
livekit.agents._exceptions.APIConnectionError: Failed to connect to Gemini Live
```

### Causa
Existem **duas formas** de definir variáveis de ambiente no Windows:
1. **Variáveis do Sistema/Usuário** - Definidas permanentemente no Windows
2. **Arquivo .env** - Definidas por projeto

**O problema:** Se a mesma variável existir nos dois lugares, a variável do sistema tem **prioridade** sobre o arquivo `.env`.

No seu caso:
- Variável do sistema tinha a chave **antiga** (expirada)
- Arquivo `.env` tinha a chave **nova** (válida)
- O sistema usava a antiga, ignorando o `.env`

### Como Diagnosticar

**Verificar variáveis do sistema:**
```powershell
# Ver variável do usuário
[System.Environment]::GetEnvironmentVariable("GOOGLE_API_KEY", "User")

# Ver variável da máquina (sistema)
[System.Environment]::GetEnvironmentVariable("GOOGLE_API_KEY", "Machine")
```

**Ver qual valor está sendo usado:**
```powershell
$env:GOOGLE_API_KEY
```

**Comparar com o arquivo .env:**
Abra o arquivo `.env` e veja se a chave é diferente.

### Solução

#### Solução Rápida (para a sessão atual)
Se você quer resolver imediatamente sem fechar o terminal:
```powershell
# Remove a variável apenas da sessão atual do terminal
Remove-Item Env:GOOGLE_API_KEY -ErrorAction SilentlyContinue

# Agora o load_dotenv() vai carregar a chave do arquivo .env
python agent.py console
```

**Nota:** Isso só funciona para a sessão atual. Se abrir um novo terminal, terá que fazer de novo.

---

#### Solução Permanente

**Opção 1: Remover a variável do USUÁRIO**
```powershell
# Remove a variável de ambiente do nível de usuário
[System.Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", $null, "User")
```

Depois, **feche e reabra o terminal** (ou o VS Code) para aplicar.

**Opção 2: Remover a variável do SISTEMA (Machine)**

Se a variável está no nível de sistema (Machine), você precisa de **permissão de administrador**.

**Via PowerShell (automático):**
```powershell
# Abre um PowerShell como admin e remove a variável
Start-Process powershell -Verb RunAs -ArgumentList '-Command "[System.Environment]::SetEnvironmentVariable(\"GOOGLE_API_KEY\", $null, \"Machine\")"'
```
Uma janela vai aparecer pedindo permissão. Clique em **Sim**.

**Via PowerShell (manual):**
1. Abra o PowerShell como Administrador (botão direito → "Executar como administrador")
2. Execute:
```powershell
[System.Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", $null, "Machine")
```

**Opção 3: Atualizar a variável ao invés de remover**
```powershell
# Define a nova chave na variável do usuário
[System.Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", "SUA_NOVA_CHAVE_AQUI", "User")

# OU no nível de sistema (requer admin)
[System.Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", "SUA_NOVA_CHAVE_AQUI", "Machine")
```

**Opção 4: Pela interface gráfica do Windows**
1. Pressione `Win + R`
2. Digite `sysdm.cpl` e pressione Enter
3. Vá em **Avançado** → **Variáveis de Ambiente**
4. Procure `GOOGLE_API_KEY` em duas seções:
   - **Variáveis de usuário** (parte de cima)
   - **Variáveis de sistema** (parte de baixo)
5. Selecione e clique em **Excluir** ou **Editar**

---

### Procedimento Completo Passo a Passo

Se você está com o erro de API key expirada, siga estes passos na ordem:

```
┌─────────────────────────────────────────────────────────────────┐
│  PASSO 1: Diagnosticar onde está a chave antiga                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Execute no PowerShell:                                         │
│                                                                 │
│  # Ver variável do usuário                                      │
│  [System.Environment]::GetEnvironmentVariable(                  │
│      "GOOGLE_API_KEY", "User")                                  │
│                                                                 │
│  # Ver variável do sistema                                      │
│  [System.Environment]::GetEnvironmentVariable(                  │
│      "GOOGLE_API_KEY", "Machine")                               │
│                                                                 │
│  # Ver valor atual na sessão                                    │
│  $env:GOOGLE_API_KEY                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  PASSO 2: Comparar com o arquivo .env                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Abra o arquivo .env e veja a chave:                            │
│  GOOGLE_API_KEY=AIzaSy...                                       │
│                                                                 │
│  Se for DIFERENTE da que apareceu no Passo 1,                   │
│  você precisa remover a variável do sistema.                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  PASSO 3: Solução Rápida (resolve agora)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Remove-Item Env:GOOGLE_API_KEY -ErrorAction SilentlyContinue   │
│                                                                 │
│  Agora execute seu script normalmente.                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  PASSO 4: Solução Permanente (evita o problema no futuro)      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Se estava em User:                                             │
│  [System.Environment]::SetEnvironmentVariable(                  │
│      "GOOGLE_API_KEY", $null, "User")                           │
│                                                                 │
│  Se estava em Machine (precisa de admin):                       │
│  Start-Process powershell -Verb RunAs -ArgumentList             │
│      '-Command "[System.Environment]::SetEnvironmentVariable(   │
│      \"GOOGLE_API_KEY\", $null, \"Machine\")"'                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### Verificar se funcionou
Após aplicar a solução permanente, **feche e reabra o terminal**, depois:
```powershell
# Ambos devem retornar vazio
[System.Environment]::GetEnvironmentVariable("GOOGLE_API_KEY", "User")
[System.Environment]::GetEnvironmentVariable("GOOGLE_API_KEY", "Machine")

# Ative o venv e execute o script
.\venv\Scripts\activate
python agent.py console

# Se funcionar, o load_dotenv() está carregando a chave do .env corretamente!
```

---

## 4. Conceitos Importantes

### O que é Virtual Environment (venv)?
É uma pasta isolada com uma cópia do Python e suas próprias bibliotecas. Isso evita conflitos entre projetos diferentes.

```
projeto/
├── venv/                  ← Ambiente virtual
│   ├── Scripts/           ← Executáveis (Windows)
│   │   ├── activate       ← Script para ativar
│   │   ├── python.exe     ← Python deste projeto
│   │   └── pip.exe        ← Pip deste projeto
│   └── Lib/               ← Bibliotecas instaladas
├── agent.py
└── .env
```

### Como saber se o venv está ativo?
Quando ativo, você verá `(venv)` no início do prompt:
```
(venv) PS C:\Users\Thiago\...\Jarvis.IA>
```

### O que é o arquivo .env?
É um arquivo de texto que guarda configurações sensíveis (API keys, senhas, URLs). Formato:
```
NOME_DA_VARIAVEL=valor
OUTRA_VARIAVEL=outro_valor
```

**IMPORTANTE:** Nunca suba o `.env` para o GitHub! Adicione-o ao `.gitignore`.

### Ordem de Prioridade das Variáveis
Quando o Python busca uma variável de ambiente:

```
1. Variáveis do Sistema (Machine) ← Maior prioridade
2. Variáveis do Usuário (User)
3. Variáveis da sessão atual
4. Arquivo .env (via load_dotenv) ← Menor prioridade*
```

*`load_dotenv()` por padrão **não sobrescreve** variáveis existentes. Para forçar:
```python
from dotenv import load_dotenv
load_dotenv(override=True)  # Força usar valores do .env
```

---

## Resumo de Comandos Úteis

| Ação | Comando |
|------|---------|
| Ativar venv | `.\venv\Scripts\activate` |
| Desativar venv | `deactivate` |
| Criar venv | `python -m venv venv` |
| Ver variável de ambiente | `$env:NOME_VARIAVEL` |
| Listar todas as variáveis | `Get-ChildItem Env:` |
| Definir variável temporária | `$env:NOME = "valor"` |
| Definir variável permanente | `[System.Environment]::SetEnvironmentVariable("NOME", "valor", "User")` |
| Remover variável permanente | `[System.Environment]::SetEnvironmentVariable("NOME", $null, "User")` |
| Ver política de execução | `Get-ExecutionPolicy -List` |

---

## Checklist Antes de Executar o Projeto

- [ ] Virtual environment está ativo? `(venv)` aparece no prompt?
- [ ] Arquivo `.env` existe e tem as chaves corretas?
- [ ] Não há variáveis de sistema sobrescrevendo o `.env`?
- [ ] As dependências estão instaladas? `pip list`

---

*Guia criado em 28/02/2026 - Projeto JARVIS*
