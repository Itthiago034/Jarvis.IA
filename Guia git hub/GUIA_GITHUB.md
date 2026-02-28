# Guia de Git e GitHub para Iniciantes

Este guia foi criado para ajudar a resolver problemas comuns com Git e GitHub.

---

## Índice

1. [Conceitos Básicos](#conceitos-básicos)
2. [Problema: Sem Permissão para Push](#problema-sem-permissão-para-push)
3. [Como Verificar sua Conta](#como-verificar-sua-conta)
4. [Como Trocar de Conta](#como-trocar-de-conta)
5. [Comandos Úteis do Dia a Dia](#comandos-úteis-do-dia-a-dia)
6. [Fluxo de Trabalho Básico](#fluxo-de-trabalho-básico)

---

## Conceitos Básicos

### O que é Git?
Git é um sistema de controle de versão. Ele salva o histórico de todas as alterações do seu código, permitindo voltar no tempo se necessário.

### O que é GitHub?
GitHub é um site que hospeda seus repositórios Git na nuvem. Pense nele como um "Google Drive para código".

### Termos Importantes

| Termo | Significado |
|-------|-------------|
| **Repositório (repo)** | Pasta do projeto com histórico de versões |
| **Commit** | Um "save" do seu código com uma mensagem descritiva |
| **Push** | Enviar commits locais para o GitHub |
| **Pull** | Baixar alterações do GitHub para seu computador |
| **Remote** | O endereço do repositório no GitHub |
| **Branch** | Uma "ramificação" do código (geralmente `main` é a principal) |

---

## Problema: Sem Permissão para Push

### Sintoma
Ao tentar fazer push, aparece uma mensagem como:
> "Você não tem permissões para efetuar push para 'usuario/repositorio' no GitHub"

### Causa
Você está logado com uma conta diferente da dona do repositório.

**Exemplo do que aconteceu:**
- Repositório pertence a: `Itthiago034`
- Conta logada era: `thiagozs-ts`
- Resultado: GitHub recusa o push

### Solução
1. Verificar qual conta está logada
2. Fazer login na conta correta
3. Tentar o push novamente

---

## Como Verificar sua Conta

### Ver qual conta está ativa
```powershell
gh auth status
```

**Saída esperada:**
```
github.com
  ✓ Logged in to github.com account Itthiago034 (keyring)
  - Active account: true    ← Esta é a conta ativa
```

### Ver para qual repositório você está enviando
```powershell
git remote -v
```

**Saída esperada:**
```
origin  https://github.com/Itthiago034/Jarvis.IA.git (fetch)
origin  https://github.com/Itthiago034/Jarvis.IA.git (push)
```

**Dica:** O nome de usuário no link (ex: `Itthiago034`) deve ser o mesmo da conta ativa no `gh auth status`.

---

## Como Trocar de Conta

### Passo 1: Iniciar o login
```powershell
gh auth login
```

### Passo 2: Responder as perguntas
Use as setas do teclado e Enter para selecionar:

1. **Where do you use GitHub?**
   - Selecione: `GitHub.com`

2. **What is your preferred protocol?**
   - Selecione: `HTTPS`

3. **Authenticate Git with your GitHub credentials?**
   - Selecione: `Y` (Yes)

4. **How would you like to authenticate?**
   - Selecione: `Login with a web browser`

### Passo 3: Usar o código no navegador
1. Um código aparecerá no terminal (ex: `ABCD-1234`)
2. Copie esse código
3. O navegador abrirá automaticamente (ou acesse: https://github.com/login/device)
4. Faça login na conta desejada
5. Cole o código quando solicitado
6. Autorize o acesso

### Passo 4: Confirmar no terminal
Pressione Enter para finalizar.

### Passo 5: Verificar
```powershell
gh auth status
```

Confirme que a conta correta está como `Active account: true`.

---

## Comandos Úteis do Dia a Dia

### Ver status das alterações
```powershell
git status
```
Mostra quais arquivos foram modificados, adicionados ou removidos.

### Adicionar arquivos para commit
```powershell
# Adicionar um arquivo específico
git add nome-do-arquivo.md

# Adicionar todos os arquivos modificados
git add .
```

### Criar um commit
```powershell
git commit -m "Descrição do que foi feito"
```

**Boas práticas para mensagens:**
- ✅ `Adiciona validação de email no formulário`
- ✅ `Corrige bug no cálculo de desconto`
- ❌ `alterações`
- ❌ `fix`

### Enviar para o GitHub (push)
```powershell
git push
```

### Baixar alterações do GitHub (pull)
```powershell
git pull
```

### Ver histórico de commits
```powershell
git log --oneline
```

---

## Fluxo de Trabalho Básico

```
┌─────────────────────────────────────────────────────────┐
│                    FLUXO DIÁRIO                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   1. Abrir o projeto                                    │
│              ↓                                          │
│   2. git pull (baixar alterações recentes)              │
│              ↓                                          │
│   3. Fazer suas alterações no código                    │
│              ↓                                          │
│   4. git add . (preparar arquivos)                      │
│              ↓                                          │
│   5. git commit -m "descrição" (salvar localmente)      │
│              ↓                                          │
│   6. git push (enviar para GitHub)                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Resumo em comandos
```powershell
git pull
# ... faz alterações ...
git add .
git commit -m "Minha alteração"
git push
```

---

## Problemas Comuns e Soluções

### "fatal: not a git repository"
**Causa:** Você não está dentro de uma pasta com Git inicializado.
**Solução:** Navegue até a pasta correta do projeto.

### "error: failed to push some refs"
**Causa:** O GitHub tem commits que você não tem localmente.
**Solução:** 
```powershell
git pull
git push
```

### "Permission denied"
**Causa:** Conta errada ou sem permissão.
**Solução:** Siga a seção [Como Trocar de Conta](#como-trocar-de-conta).

---

## Links Úteis

- [Documentação Oficial do Git](https://git-scm.com/doc)
- [GitHub Docs](https://docs.github.com/pt)
- [GitHub CLI (gh)](https://cli.github.com/manual/)

---

*Guia criado em 28/02/2026 - Projeto JARVIS*
