"""
JARVIS - Database Tools
=======================
Ferramentas para interação com bancos de dados.
Suporta SQLite, PostgreSQL, MySQL, MongoDB.
"""

import os
import json
import asyncio
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
from datetime import datetime


class DatabaseTools:
    """Ferramentas para bancos de dados"""
    
    def __init__(self):
        self._connections: Dict[str, Any] = {}
    
    # ==================== SQLITE ====================
    
    async def sqlite_query(self, db_path: str, query: str) -> List[Dict]:
        """Executa query SQLite"""
        import aiosqlite  # type: ignore[reportMissingImports]
        
        async with aiosqlite.connect(db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def sqlite_execute(self, db_path: str, query: str, params: tuple = ()) -> int:
        """Executa comando SQLite (INSERT, UPDATE, DELETE)"""
        import aiosqlite  # type: ignore[reportMissingImports]
        
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute(query, params)
            await db.commit()
            return cursor.rowcount
    
    async def sqlite_get_schema(self, db_path: str) -> Dict[str, List[Dict]]:
        """Obtém schema do banco SQLite"""
        import aiosqlite  # type: ignore[reportMissingImports]
        
        schema = {}
        async with aiosqlite.connect(db_path) as db:
            # Obter tabelas
            async with db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ) as cursor:
                tables = await cursor.fetchall()
            
            for (table_name,) in tables:
                async with db.execute(f"PRAGMA table_info({table_name})") as cursor:
                    columns = await cursor.fetchall()
                    schema[table_name] = [
                        {
                            "name": col[1],
                            "type": col[2],
                            "nullable": not col[3],
                            "primary_key": bool(col[5])
                        }
                        for col in columns
                    ]
        
        return schema
    
    # ==================== POSTGRESQL ====================
    
    async def postgres_query(self, connection_string: str, query: str) -> List[Dict]:
        """Executa query PostgreSQL"""
        try:
            import asyncpg  # type: ignore[reportMissingImports]
            
            conn = await asyncpg.connect(connection_string)
            try:
                rows = await conn.fetch(query)
                return [dict(row) for row in rows]
            finally:
                await conn.close()
        except ImportError:
            return [{"error": "asyncpg não instalado. Execute: pip install asyncpg"}]
    
    async def postgres_execute(self, connection_string: str, query: str) -> str:
        """Executa comando PostgreSQL"""
        try:
            import asyncpg  # type: ignore[reportMissingImports]
            
            conn = await asyncpg.connect(connection_string)
            try:
                result = await conn.execute(query)
                return result
            finally:
                await conn.close()
        except ImportError:
            return "asyncpg não instalado"
    
    async def postgres_get_schema(self, connection_string: str) -> Dict[str, List[Dict]]:
        """Obtém schema PostgreSQL"""
        try:
            import asyncpg  # type: ignore[reportMissingImports]
            
            conn = await asyncpg.connect(connection_string)
            try:
                # Query para obter schema
                query = """
                SELECT table_name, column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position
                """
                rows = await conn.fetch(query)
                
                schema = {}
                for row in rows:
                    table = row['table_name']
                    if table not in schema:
                        schema[table] = []
                    schema[table].append({
                        "name": row['column_name'],
                        "type": row['data_type'],
                        "nullable": row['is_nullable'] == 'YES',
                        "default": row['column_default']
                    })
                return schema
            finally:
                await conn.close()
        except ImportError:
            return {"error": ["asyncpg não instalado"]}
    
    # ==================== MONGODB ====================
    
    async def mongodb_query(self, uri: str, database: str, collection: str,
                           query: Dict = None, limit: int = 100) -> List[Dict]:
        """Executa query MongoDB"""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient  # type: ignore[reportMissingImports]
            
            client = AsyncIOMotorClient(uri)
            db = client[database]
            coll = db[collection]
            
            cursor = coll.find(query or {}).limit(limit)
            docs = await cursor.to_list(length=limit)
            
            # Converter ObjectId para string
            for doc in docs:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            
            client.close()
            return docs
        except ImportError:
            return [{"error": "motor não instalado. Execute: pip install motor"}]
    
    async def mongodb_insert(self, uri: str, database: str, collection: str,
                            document: Dict) -> str:
        """Insere documento no MongoDB"""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient  # type: ignore[reportMissingImports]
            
            client = AsyncIOMotorClient(uri)
            db = client[database]
            coll = db[collection]
            
            result = await coll.insert_one(document)
            client.close()
            
            return str(result.inserted_id)
        except ImportError:
            return "motor não instalado"
    
    async def mongodb_get_collections(self, uri: str, database: str) -> List[str]:
        """Lista collections do MongoDB"""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient  # type: ignore[reportMissingImports]
            
            client = AsyncIOMotorClient(uri)
            db = client[database]
            collections = await db.list_collection_names()
            client.close()
            
            return collections
        except ImportError:
            return ["motor não instalado"]


class NaturalLanguageSQL:
    """Converte linguagem natural para SQL"""
    
    TEMPLATES = {
        # Padrões comuns em português
        r"mostre?\s+(?:todos?\s+)?(?:os?\s+)?(.+?)(?:\s+da\s+tabela\s+)?(\w+)": 
            "SELECT {0} FROM {1}",
        
        r"quantos?\s+(.+?)(?:\s+existem?\s+)?(?:na?\s+tabela\s+)?(\w+)":
            "SELECT COUNT(*) FROM {1}",
        
        r"(?:usuários?|clientes?|registros?)\s+criados?\s+hoje":
            "SELECT * FROM {table} WHERE DATE(created_at) = DATE('now')",
        
        r"(?:últimos?|recentes?)\s+(\d+)\s+(.+)":
            "SELECT * FROM {1} ORDER BY created_at DESC LIMIT {0}",
        
        r"(.+?)\s+onde\s+(.+?)\s*=\s*['\"]?(.+?)['\"]?$":
            "SELECT * FROM {0} WHERE {1} = '{2}'",
    }
    
    @classmethod
    def to_sql(cls, natural_query: str, schema: Dict = None) -> str:
        """Tenta converter query natural para SQL"""
        import re
        
        query = natural_query.lower().strip()
        
        # Tentar padrões conhecidos
        for pattern, template in cls.TEMPLATES.items():
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                groups = match.groups()
                sql = template
                for i, g in enumerate(groups):
                    sql = sql.replace(f"{{{i}}}", g)
                return sql
        
        # Se não encontrou padrão, retornar sugestão genérica
        return f"-- Não foi possível converter: {natural_query}\n-- Tente: SELECT * FROM tabela WHERE coluna = 'valor'"


# ==================== FUNÇÕES DE FERRAMENTA PARA O AGENTE ====================

def get_database_tools():
    """Retorna as ferramentas de banco de dados para o CodeAgent"""
    db = DatabaseTools()
    nl_sql = NaturalLanguageSQL()
    
    async def sqlite_query(db_path: str, query: str) -> str:
        """
        Executa query SQL em banco SQLite.
        
        Args:
            db_path: Caminho para o arquivo .db ou .sqlite
            query: Query SQL a executar
        
        Returns:
            Resultados da query formatados
        """
        path = Path(db_path)
        if not path.exists():
            return f"❌ Banco de dados não encontrado: {db_path}"
        
        try:
            results = await db.sqlite_query(db_path, query)
            
            if not results:
                return "Nenhum resultado encontrado"
            
            # Formatar como tabela
            output = [f"📊 Resultados ({len(results)} linhas):\n"]
            
            # Headers
            headers = list(results[0].keys())
            output.append(" | ".join(headers))
            output.append("-" * (len(" | ".join(headers))))
            
            # Rows
            for row in results[:50]:
                output.append(" | ".join(str(row.get(h, ""))[:30] for h in headers))
            
            if len(results) > 50:
                output.append(f"\n... e mais {len(results) - 50} linhas")
            
            return "\n".join(output)
        except Exception as e:
            return f"❌ Erro na query: {e}"
    
    async def sqlite_schema(db_path: str) -> str:
        """
        Mostra o schema de um banco SQLite.
        
        Args:
            db_path: Caminho para o arquivo .db
        
        Returns:
            Schema do banco
        """
        path = Path(db_path)
        if not path.exists():
            return f"❌ Banco não encontrado: {db_path}"
        
        try:
            schema = await db.sqlite_get_schema(db_path)
            
            output = [f"📋 Schema de {path.name}:\n"]
            for table, columns in schema.items():
                output.append(f"\n📁 {table}:")
                for col in columns:
                    pk = "🔑" if col['primary_key'] else ""
                    nullable = "?" if col['nullable'] else ""
                    output.append(f"  • {col['name']} ({col['type']}) {pk}{nullable}")
            
            return "\n".join(output)
        except Exception as e:
            return f"❌ Erro: {e}"
    
    async def sqlite_execute(db_path: str, command: str) -> str:
        """
        Executa comando SQL (INSERT, UPDATE, DELETE).
        
        Args:
            db_path: Caminho para o arquivo .db
            command: Comando SQL
        
        Returns:
            Número de linhas afetadas
        """
        try:
            affected = await db.sqlite_execute(db_path, command)
            return f"✅ {affected} linha(s) afetada(s)"
        except Exception as e:
            return f"❌ Erro: {e}"
    
    async def postgres_query(connection_string: str, query: str) -> str:
        """
        Executa query em PostgreSQL.
        
        Args:
            connection_string: String de conexão (postgresql://user:pass@host:port/db)
            query: Query SQL
        
        Returns:
            Resultados formatados
        """
        try:
            results = await db.postgres_query(connection_string, query)
            
            if "error" in results[0] if results else False:
                return f"❌ {results[0]['error']}"
            
            if not results:
                return "Nenhum resultado"
            
            output = [f"📊 Resultados ({len(results)} linhas):\n"]
            headers = list(results[0].keys())
            output.append(" | ".join(headers))
            output.append("-" * 50)
            
            for row in results[:50]:
                output.append(" | ".join(str(row.get(h, ""))[:25] for h in headers))
            
            return "\n".join(output)
        except Exception as e:
            return f"❌ Erro: {e}"
    
    async def postgres_schema(connection_string: str) -> str:
        """
        Mostra schema do PostgreSQL.
        
        Args:
            connection_string: String de conexão
        
        Returns:
            Schema do banco
        """
        try:
            schema = await db.postgres_get_schema(connection_string)
            
            if "error" in schema:
                return f"❌ {schema['error']}"
            
            output = ["📋 Schema PostgreSQL:\n"]
            for table, columns in schema.items():
                output.append(f"\n📁 {table}:")
                for col in columns:
                    nullable = "?" if col['nullable'] else ""
                    output.append(f"  • {col['name']} ({col['type']}) {nullable}")
            
            return "\n".join(output)
        except Exception as e:
            return f"❌ Erro: {e}"
    
    async def mongodb_query(uri: str, database: str, collection: str,
                           query_json: str = "{}") -> str:
        """
        Executa query no MongoDB.
        
        Args:
            uri: URI de conexão (mongodb://localhost:27017)
            database: Nome do banco
            collection: Nome da collection
            query_json: Query em JSON (ex: {"status": "active"})
        
        Returns:
            Documentos encontrados
        """
        try:
            query = json.loads(query_json) if query_json else {}
            results = await db.mongodb_query(uri, database, collection, query)
            
            if results and "error" in results[0]:
                return f"❌ {results[0]['error']}"
            
            if not results:
                return "Nenhum documento encontrado"
            
            output = [f"📊 Documentos ({len(results)}):\n"]
            for doc in results[:20]:
                output.append(json.dumps(doc, indent=2, default=str)[:500])
                output.append("---")
            
            return "\n".join(output)
        except json.JSONDecodeError:
            return "❌ Query JSON inválida"
        except Exception as e:
            return f"❌ Erro: {e}"
    
    async def mongodb_collections(uri: str, database: str) -> str:
        """
        Lista collections do MongoDB.
        
        Args:
            uri: URI de conexão
            database: Nome do banco
        
        Returns:
            Lista de collections
        """
        try:
            collections = await db.mongodb_get_collections(uri, database)
            
            if collections and collections[0] == "motor não instalado":
                return "❌ motor não instalado. Execute: pip install motor"
            
            output = [f"📁 Collections em {database}:\n"]
            for coll in collections:
                output.append(f"  • {coll}")
            
            return "\n".join(output)
        except Exception as e:
            return f"❌ Erro: {e}"
    
    def natural_to_sql(query: str) -> str:
        """
        Converte query em linguagem natural para SQL.
        
        Args:
            query: Query em português (ex: "mostre todos usuários")
        
        Returns:
            Query SQL correspondente
        """
        sql = nl_sql.to_sql(query)
        return f"🔄 Conversão:\n\n```sql\n{sql}\n```"
    
    return {
        "sqlite_query": sqlite_query,
        "sqlite_schema": sqlite_schema,
        "sqlite_execute": sqlite_execute,
        "postgres_query": postgres_query,
        "postgres_schema": postgres_schema,
        "mongodb_query": mongodb_query,
        "mongodb_collections": mongodb_collections,
        "natural_to_sql": natural_to_sql,
    }
