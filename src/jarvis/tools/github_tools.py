"""
JARVIS - GitHub Tools
=====================
Ferramentas para integração com GitHub.
Gerencia repositórios, issues, PRs, branches e mais.
"""

import os
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import aiohttp  # type: ignore[reportMissingImports]


@dataclass
class GitHubConfig:
    """Configuração do GitHub"""
    token: str
    owner: Optional[str] = None
    repo: Optional[str] = None
    api_base: str = "https://api.github.com"


class GitHubTools:
    """Ferramentas para interação com GitHub API"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.api_base = "https://api.github.com"
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtém ou cria sessão HTTP"""
        if self._session is None or self._session.closed:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            self._session = aiohttp.ClientSession(headers=headers)
        return self._session
    
    async def close(self):
        """Fecha a sessão"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    # ==================== REPOSITÓRIOS ====================
    
    async def get_repo_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Obtém informações do repositório"""
        session = await self._get_session()
        async with session.get(f"{self.api_base}/repos/{owner}/{repo}") as resp:
            if resp.status == 200:
                return await resp.json()
            return {"error": f"Status {resp.status}", "message": await resp.text()}
    
    async def list_repos(self, username: Optional[str] = None, org: Optional[str] = None) -> List[Dict]:
        """Lista repositórios do usuário ou organização"""
        session = await self._get_session()
        
        if org:
            url = f"{self.api_base}/orgs/{org}/repos"
        elif username:
            url = f"{self.api_base}/users/{username}/repos"
        else:
            url = f"{self.api_base}/user/repos"
        
        async with session.get(url, params={"per_page": 100, "sort": "updated"}) as resp:
            if resp.status == 200:
                return await resp.json()
            return []
    
    async def create_repo(self, name: str, description: str = "", private: bool = False) -> Dict:
        """Cria um novo repositório"""
        session = await self._get_session()
        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": True
        }
        async with session.post(f"{self.api_base}/user/repos", json=data) as resp:
            return await resp.json()
    
    # ==================== ISSUES ====================
    
    async def list_issues(self, owner: str, repo: str, state: str = "open") -> List[Dict]:
        """Lista issues do repositório"""
        session = await self._get_session()
        params = {"state": state, "per_page": 50}
        async with session.get(f"{self.api_base}/repos/{owner}/{repo}/issues", params=params) as resp:
            if resp.status == 200:
                return await resp.json()
            return []
    
    async def get_issue(self, owner: str, repo: str, issue_number: int) -> Dict:
        """Obtém detalhes de uma issue"""
        session = await self._get_session()
        async with session.get(f"{self.api_base}/repos/{owner}/{repo}/issues/{issue_number}") as resp:
            return await resp.json()
    
    async def create_issue(self, owner: str, repo: str, title: str, body: str = "",
                          labels: Optional[List[str]] = None, assignees: Optional[List[str]] = None) -> Dict:
        """Cria uma nova issue"""
        session = await self._get_session()
        data = {
            "title": title,
            "body": body,
            "labels": labels or [],
            "assignees": assignees or []
        }
        async with session.post(f"{self.api_base}/repos/{owner}/{repo}/issues", json=data) as resp:
            return await resp.json()
    
    async def close_issue(self, owner: str, repo: str, issue_number: int, comment: str = "") -> Dict:
        """Fecha uma issue"""
        session = await self._get_session()
        
        # Adicionar comentário se fornecido
        if comment:
            await self.add_comment(owner, repo, issue_number, comment)
        
        # Fechar a issue
        data = {"state": "closed"}
        async with session.patch(
            f"{self.api_base}/repos/{owner}/{repo}/issues/{issue_number}", json=data
        ) as resp:
            return await resp.json()
    
    async def add_comment(self, owner: str, repo: str, issue_number: int, body: str) -> Dict:
        """Adiciona comentário a uma issue/PR"""
        session = await self._get_session()
        data = {"body": body}
        async with session.post(
            f"{self.api_base}/repos/{owner}/{repo}/issues/{issue_number}/comments", json=data
        ) as resp:
            return await resp.json()
    
    # ==================== PULL REQUESTS ====================
    
    async def list_pull_requests(self, owner: str, repo: str, state: str = "open") -> List[Dict]:
        """Lista Pull Requests"""
        session = await self._get_session()
        params = {"state": state, "per_page": 50}
        async with session.get(f"{self.api_base}/repos/{owner}/{repo}/pulls", params=params) as resp:
            if resp.status == 200:
                return await resp.json()
            return []
    
    async def get_pull_request(self, owner: str, repo: str, pr_number: int) -> Dict:
        """Obtém detalhes de um PR"""
        session = await self._get_session()
        async with session.get(f"{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}") as resp:
            return await resp.json()
    
    async def create_pull_request(self, owner: str, repo: str, title: str, body: str,
                                  head: str, base: str = "main") -> Dict:
        """Cria um Pull Request"""
        session = await self._get_session()
        data = {
            "title": title,
            "body": body,
            "head": head,
            "base": base
        }
        async with session.post(f"{self.api_base}/repos/{owner}/{repo}/pulls", json=data) as resp:
            return await resp.json()
    
    async def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """Obtém o diff de um PR"""
        session = await self._get_session()
        headers = {"Accept": "application/vnd.github.v3.diff"}
        async with session.get(
            f"{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}",
            headers=headers
        ) as resp:
            if resp.status == 200:
                return await resp.text()
            return ""
    
    async def merge_pull_request(self, owner: str, repo: str, pr_number: int,
                                 merge_method: str = "squash", commit_message: str = "") -> Dict:
        """Faz merge de um PR"""
        session = await self._get_session()
        data = {"merge_method": merge_method}
        if commit_message:
            data["commit_message"] = commit_message
        
        async with session.put(
            f"{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}/merge", json=data
        ) as resp:
            return await resp.json()
    
    async def review_pull_request(self, owner: str, repo: str, pr_number: int,
                                  body: str, event: str = "COMMENT") -> Dict:
        """Adiciona review a um PR (APPROVE, REQUEST_CHANGES, COMMENT)"""
        session = await self._get_session()
        data = {"body": body, "event": event}
        async with session.post(
            f"{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}/reviews", json=data
        ) as resp:
            return await resp.json()
    
    # ==================== BRANCHES ====================
    
    async def list_branches(self, owner: str, repo: str) -> List[Dict]:
        """Lista branches do repositório"""
        session = await self._get_session()
        async with session.get(f"{self.api_base}/repos/{owner}/{repo}/branches") as resp:
            if resp.status == 200:
                return await resp.json()
            return []
    
    async def create_branch(self, owner: str, repo: str, branch_name: str, from_branch: str = "main") -> Dict:
        """Cria uma nova branch"""
        session = await self._get_session()
        
        # Obter SHA da branch de origem
        async with session.get(f"{self.api_base}/repos/{owner}/{repo}/git/refs/heads/{from_branch}") as resp:
            if resp.status != 200:
                return {"error": f"Branch {from_branch} não encontrada"}
            ref_data = await resp.json()
            sha = ref_data["object"]["sha"]
        
        # Criar nova branch
        data = {"ref": f"refs/heads/{branch_name}", "sha": sha}
        async with session.post(f"{self.api_base}/repos/{owner}/{repo}/git/refs", json=data) as resp:
            return await resp.json()
    
    async def delete_branch(self, owner: str, repo: str, branch_name: str) -> bool:
        """Deleta uma branch"""
        session = await self._get_session()
        async with session.delete(
            f"{self.api_base}/repos/{owner}/{repo}/git/refs/heads/{branch_name}"
        ) as resp:
            return resp.status == 204
    
    # ==================== WORKFLOWS (Actions) ====================
    
    async def list_workflows(self, owner: str, repo: str) -> List[Dict]:
        """Lista workflows do GitHub Actions"""
        session = await self._get_session()
        async with session.get(f"{self.api_base}/repos/{owner}/{repo}/actions/workflows") as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("workflows", [])
            return []
    
    async def list_workflow_runs(self, owner: str, repo: str, workflow_id: Optional[int] = None) -> List[Dict]:
        """Lista execuções de workflows"""
        session = await self._get_session()
        
        if workflow_id:
            url = f"{self.api_base}/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            url = f"{self.api_base}/repos/{owner}/{repo}/actions/runs"
        
        async with session.get(url, params={"per_page": 20}) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("workflow_runs", [])
            return []
    
    async def trigger_workflow(self, owner: str, repo: str, workflow_id: int, ref: str = "main",
                               inputs: Optional[Dict] = None) -> bool:
        """Dispara um workflow manualmente"""
        session = await self._get_session()
        data = {"ref": ref}
        if inputs:
            data["inputs"] = inputs
        
        async with session.post(
            f"{self.api_base}/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
            json=data
        ) as resp:
            return resp.status == 204
    
    # ==================== BUSCA ====================
    
    async def search_code(self, query: str, owner: Optional[str] = None, repo: Optional[str] = None) -> List[Dict]:
        """Busca código no GitHub"""
        session = await self._get_session()
        
        search_query = query
        if owner and repo:
            search_query += f" repo:{owner}/{repo}"
        elif owner:
            search_query += f" user:{owner}"
        
        params = {"q": search_query, "per_page": 30}
        async with session.get(f"{self.api_base}/search/code", params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("items", [])
            return []
    
    async def search_issues(self, query: str, owner: Optional[str] = None, 
                           repo: Optional[str] = None, is_pr: bool = False) -> List[Dict]:
        """Busca issues ou PRs"""
        session = await self._get_session()
        
        search_query = query
        if owner and repo:
            search_query += f" repo:{owner}/{repo}"
        if is_pr:
            search_query += " is:pr"
        else:
            search_query += " is:issue"
        
        params = {"q": search_query, "per_page": 30}
        async with session.get(f"{self.api_base}/search/issues", params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("items", [])
            return []
    
    # ==================== UTILITÁRIOS ====================
    
    async def get_authenticated_user(self) -> Dict:
        """Obtém informações do usuário autenticado"""
        session = await self._get_session()
        async with session.get(f"{self.api_base}/user") as resp:
            return await resp.json()
    
    async def get_rate_limit(self) -> Dict:
        """Verifica limite de requisições da API"""
        session = await self._get_session()
        async with session.get(f"{self.api_base}/rate_limit") as resp:
            return await resp.json()


# ==================== FUNÇÕES DE FERRAMENTA PARA O AGENTE ====================

def get_github_tools():
    """Retorna as ferramentas do GitHub para o CodeAgent"""
    github = GitHubTools()
    
    async def github_list_issues(owner: str, repo: str, state: str = "open") -> str:
        """
        Lista issues de um repositório GitHub.
        
        Args:
            owner: Dono do repositório (ex: "microsoft")
            repo: Nome do repositório (ex: "vscode")
            state: Estado das issues ("open", "closed", "all")
        
        Returns:
            Lista formatada de issues
        """
        issues = await github.list_issues(owner, repo, state)
        if not issues:
            return f"Nenhuma issue {state} encontrada em {owner}/{repo}"
        
        result = [f"📋 Issues ({state}) em {owner}/{repo}:\n"]
        for issue in issues[:20]:
            labels = ", ".join([l["name"] for l in issue.get("labels", [])])
            result.append(
                f"  #{issue['number']} - {issue['title']}\n"
                f"     Estado: {issue['state']} | Labels: {labels or 'nenhum'}\n"
                f"     URL: {issue['html_url']}\n"
            )
        return "\n".join(result)
    
    async def github_create_issue(owner: str, repo: str, title: str, body: str = "",
                                  labels: str = "") -> str:
        """
        Cria uma nova issue no GitHub.
        
        Args:
            owner: Dono do repositório
            repo: Nome do repositório
            title: Título da issue
            body: Corpo/descrição da issue (Markdown)
            labels: Labels separados por vírgula (ex: "bug,priority-high")
        
        Returns:
            Informações da issue criada
        """
        label_list = [l.strip() for l in labels.split(",") if l.strip()] if labels else None
        result = await github.create_issue(owner, repo, title, body, label_list)
        
        if "number" in result:
            return f"✅ Issue #{result['number']} criada com sucesso!\nURL: {result['html_url']}"
        return f"❌ Erro ao criar issue: {result}"
    
    async def github_list_prs(owner: str, repo: str, state: str = "open") -> str:
        """
        Lista Pull Requests de um repositório.
        
        Args:
            owner: Dono do repositório
            repo: Nome do repositório
            state: Estado dos PRs ("open", "closed", "all")
        
        Returns:
            Lista formatada de PRs
        """
        prs = await github.list_pull_requests(owner, repo, state)
        if not prs:
            return f"Nenhum PR {state} encontrado em {owner}/{repo}"
        
        result = [f"🔀 Pull Requests ({state}) em {owner}/{repo}:\n"]
        for pr in prs[:20]:
            result.append(
                f"  #{pr['number']} - {pr['title']}\n"
                f"     {pr['head']['ref']} → {pr['base']['ref']}\n"
                f"     Autor: {pr['user']['login']} | Estado: {pr['state']}\n"
                f"     URL: {pr['html_url']}\n"
            )
        return "\n".join(result)
    
    async def github_create_pr(owner: str, repo: str, title: str, body: str,
                               head: str, base: str = "main") -> str:
        """
        Cria um Pull Request.
        
        Args:
            owner: Dono do repositório
            repo: Nome do repositório
            title: Título do PR
            body: Descrição do PR (Markdown)
            head: Branch de origem (com suas mudanças)
            base: Branch de destino (padrão: main)
        
        Returns:
            Informações do PR criado
        """
        result = await github.create_pull_request(owner, repo, title, body, head, base)
        
        if "number" in result:
            return f"✅ PR #{result['number']} criado!\nURL: {result['html_url']}"
        return f"❌ Erro: {result.get('message', result)}"
    
    async def github_review_pr(owner: str, repo: str, pr_number: int, 
                               review_body: str, action: str = "COMMENT") -> str:
        """
        Adiciona review a um Pull Request.
        
        Args:
            owner: Dono do repositório
            repo: Nome do repositório
            pr_number: Número do PR
            review_body: Conteúdo do review
            action: Tipo de review (APPROVE, REQUEST_CHANGES, COMMENT)
        
        Returns:
            Confirmação do review
        """
        result = await github.review_pull_request(owner, repo, pr_number, review_body, action)
        
        if "id" in result:
            return f"✅ Review adicionado ao PR #{pr_number} ({action})"
        return f"❌ Erro: {result.get('message', result)}"
    
    async def github_get_pr_diff(owner: str, repo: str, pr_number: int) -> str:
        """
        Obtém o diff de um Pull Request para análise.
        
        Args:
            owner: Dono do repositório
            repo: Nome do repositório
            pr_number: Número do PR
        
        Returns:
            Diff do PR
        """
        diff = await github.get_pr_diff(owner, repo, pr_number)
        if diff:
            # Limitar tamanho para não sobrecarregar
            if len(diff) > 10000:
                diff = diff[:10000] + "\n\n... [diff truncado, muito grande]"
            return f"📝 Diff do PR #{pr_number}:\n\n```diff\n{diff}\n```"
        return f"❌ Não foi possível obter o diff do PR #{pr_number}"
    
    async def github_list_branches(owner: str, repo: str) -> str:
        """
        Lista branches de um repositório.
        
        Args:
            owner: Dono do repositório
            repo: Nome do repositório
        
        Returns:
            Lista de branches
        """
        branches = await github.list_branches(owner, repo)
        if not branches:
            return f"Nenhuma branch encontrada em {owner}/{repo}"
        
        result = [f"🌿 Branches em {owner}/{repo}:\n"]
        for branch in branches:
            protected = "🔒" if branch.get("protected") else ""
            result.append(f"  • {branch['name']} {protected}")
        return "\n".join(result)
    
    async def github_create_branch(owner: str, repo: str, branch_name: str,
                                   from_branch: str = "main") -> str:
        """
        Cria uma nova branch.
        
        Args:
            owner: Dono do repositório
            repo: Nome do repositório
            branch_name: Nome da nova branch
            from_branch: Branch de origem (padrão: main)
        
        Returns:
            Confirmação da criação
        """
        result = await github.create_branch(owner, repo, branch_name, from_branch)
        
        if "ref" in result:
            return f"✅ Branch '{branch_name}' criada a partir de '{from_branch}'"
        return f"❌ Erro: {result.get('message', result)}"
    
    async def github_search_code(query: str, owner: str = "", repo: str = "") -> str:
        """
        Busca código no GitHub.
        
        Args:
            query: Termo de busca (ex: "async def" ou "TODO fix")
            owner: Filtrar por usuário/organização (opcional)
            repo: Filtrar por repositório (opcional)
        
        Returns:
            Resultados da busca
        """
        results = await github.search_code(query, owner or None, repo or None)
        if not results:
            return f"Nenhum resultado para: {query}"
        
        output = [f"🔍 Resultados para '{query}':\n"]
        for item in results[:15]:
            output.append(
                f"  📄 {item['repository']['full_name']}/{item['path']}\n"
                f"     URL: {item['html_url']}\n"
            )
        return "\n".join(output)
    
    async def github_workflow_status(owner: str, repo: str) -> str:
        """
        Verifica status dos workflows do GitHub Actions.
        
        Args:
            owner: Dono do repositório
            repo: Nome do repositório
        
        Returns:
            Status das últimas execuções
        """
        runs = await github.list_workflow_runs(owner, repo)
        if not runs:
            return f"Nenhum workflow encontrado em {owner}/{repo}"
        
        result = [f"⚙️ GitHub Actions - {owner}/{repo}:\n"]
        for run in runs[:10]:
            status_emoji = {
                "completed": "✅" if run["conclusion"] == "success" else "❌",
                "in_progress": "🔄",
                "queued": "⏳"
            }.get(run["status"], "❓")
            
            result.append(
                f"  {status_emoji} {run['name']}\n"
                f"     Branch: {run['head_branch']} | {run['status']}\n"
                f"     URL: {run['html_url']}\n"
            )
        return "\n".join(result)
    
    return {
        "github_list_issues": github_list_issues,
        "github_create_issue": github_create_issue,
        "github_list_prs": github_list_prs,
        "github_create_pr": github_create_pr,
        "github_review_pr": github_review_pr,
        "github_get_pr_diff": github_get_pr_diff,
        "github_list_branches": github_list_branches,
        "github_create_branch": github_create_branch,
        "github_search_code": github_search_code,
        "github_workflow_status": github_workflow_status,
    }
