"""
JARVIS - Diagram Tools
======================
Ferramentas para gerar diagramas de arquitetura, fluxo, sequência, etc.
Usa Mermaid para geração de diagramas em texto.
"""

import ast
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DiagramConfig:
    """Configuração do diagrama"""
    title: Optional[str] = None
    direction: str = "TD"  # TD, LR, BT, RL
    theme: str = "default"  # default, dark, forest, neutral


def generate_flowchart(
    title: str,
    steps: List[Dict[str, str]],
    direction: str = "TD"
) -> str:
    """
    Gera um diagrama de fluxo.
    
    Args:
        title: Título do diagrama
        steps: Lista de passos [{"id": "A", "text": "Start", "type": "start"}]
               Tipos: start, end, process, decision, io, subroutine
        direction: TD (top-down), LR (left-right), BT, RL
        
    Returns:
        Código Mermaid do diagrama
        
    Exemplo:
        steps = [
            {"id": "A", "text": "Início", "type": "start"},
            {"id": "B", "text": "Processar dados", "type": "process"},
            {"id": "C", "text": "Dados válidos?", "type": "decision"},
            {"id": "D", "text": "Salvar", "type": "process"},
            {"id": "E", "text": "Erro", "type": "io"},
            {"id": "F", "text": "Fim", "type": "end"}
        ]
        connections = [("A", "B"), ("B", "C"), ("C", "D", "Sim"), ("C", "E", "Não"), ("D", "F"), ("E", "F")]
    """
    mermaid = [f"---", f"title: {title}", f"---", f"flowchart {direction}"]
    
    # Mapear tipos de nó para formato Mermaid
    type_formats = {
        "start": ("([", "])"),      # Stadium
        "end": ("([", "])"),
        "process": ("[", "]"),       # Retângulo
        "decision": ("{", "}"),      # Losango
        "io": ("[/", "/]"),          # Paralelogramo
        "subroutine": ("[[", "]]"),  # Subrotina
        "database": ("[(", ")]"),    # Cilindro
        "circle": ("((", "))"),      # Círculo
    }
    
    for step in steps:
        node_id = step.get("id", "")
        text = step.get("text", "")
        node_type = step.get("type", "process")
        prefix, suffix = type_formats.get(node_type, ("[", "]"))
        mermaid.append(f"    {node_id}{prefix}{text}{suffix}")
    
    return "\n".join(mermaid)


def add_flowchart_connections(
    base_diagram: str,
    connections: List[tuple]
) -> str:
    """
    Adiciona conexões a um diagrama de fluxo.
    
    Args:
        base_diagram: Diagrama base
        connections: Lista de conexões [("A", "B"), ("B", "C", "label")]
        
    Returns:
        Diagrama completo
    """
    lines = base_diagram.split("\n")
    
    for conn in connections:
        if len(conn) == 2:
            lines.append(f"    {conn[0]} --> {conn[1]}")
        elif len(conn) == 3:
            lines.append(f"    {conn[0]} -->|{conn[2]}| {conn[1]}")
    
    return "\n".join(lines)


def generate_sequence_diagram(
    title: str,
    participants: List[str],
    messages: List[Dict[str, str]]
) -> str:
    """
    Gera um diagrama de sequência.
    
    Args:
        title: Título do diagrama
        participants: Lista de participantes
        messages: Lista de mensagens [{"from": "A", "to": "B", "text": "Request", "type": "sync"}]
                  Tipos: sync (->), async (->>), response (-->), note
                  
    Returns:
        Código Mermaid
    """
    mermaid = [f"---", f"title: {title}", f"---", "sequenceDiagram"]
    
    # Participantes
    for p in participants:
        mermaid.append(f"    participant {p}")
    
    mermaid.append("")
    
    # Mensagens
    arrow_types = {
        "sync": "->>",
        "async": "-))",
        "response": "-->>",
        "dotted": "-->",
    }
    
    for msg in messages:
        from_p = msg.get("from", "")
        to_p = msg.get("to", "")
        text = msg.get("text", "")
        msg_type = msg.get("type", "sync")
        
        if msg_type == "note":
            position = msg.get("position", "right")
            mermaid.append(f"    Note {position} of {from_p}: {text}")
        elif msg_type == "activate":
            mermaid.append(f"    activate {from_p}")
        elif msg_type == "deactivate":
            mermaid.append(f"    deactivate {from_p}")
        else:
            arrow = arrow_types.get(msg_type, "->>")
            mermaid.append(f"    {from_p}{arrow}{to_p}: {text}")
    
    return "\n".join(mermaid)


def generate_class_diagram(
    title: str,
    classes: List[Dict[str, Any]],
    relationships: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Gera um diagrama de classes.
    
    Args:
        title: Título
        classes: Lista de classes [{"name": "User", "attributes": ["id", "name"], "methods": ["save()"]}]
        relationships: Relações [{"from": "User", "to": "Order", "type": "1--*", "label": "has"}]
        
    Returns:
        Código Mermaid
    """
    mermaid = [f"---", f"title: {title}", f"---", "classDiagram"]
    
    for cls in classes:
        name = cls.get("name", "Class")
        
        # Classe
        mermaid.append(f"    class {name} {{")
        
        # Atributos
        for attr in cls.get("attributes", []):
            visibility = "+"  # public por padrão
            if attr.startswith("_"):
                visibility = "-"  # private
            mermaid.append(f"        {visibility}{attr}")
        
        # Métodos
        for method in cls.get("methods", []):
            visibility = "+"
            if method.startswith("_"):
                visibility = "-"
            mermaid.append(f"        {visibility}{method}")
        
        mermaid.append("    }")
    
    # Relacionamentos
    if relationships:
        mermaid.append("")
        relation_types = {
            "inheritance": "<|--",      # Herança
            "composition": "*--",       # Composição
            "aggregation": "o--",       # Agregação
            "association": "-->",       # Associação
            "dependency": "..>",        # Dependência
            "realization": "..|>",      # Realização
        }
        
        for rel in relationships:
            from_cls = rel.get("from", "")
            to_cls = rel.get("to", "")
            rel_type = rel.get("type", "association")
            label = rel.get("label", "")
            
            arrow = relation_types.get(rel_type, "-->")
            if label:
                mermaid.append(f"    {from_cls} {arrow} {to_cls} : {label}")
            else:
                mermaid.append(f"    {from_cls} {arrow} {to_cls}")
    
    return "\n".join(mermaid)


def generate_er_diagram(
    title: str,
    entities: List[Dict[str, Any]],
    relationships: List[Dict[str, str]]
) -> str:
    """
    Gera um diagrama Entidade-Relacionamento.
    
    Args:
        title: Título
        entities: Entidades [{"name": "User", "attributes": [{"name": "id", "type": "int", "pk": True}]}]
        relationships: Relações [{"from": "User", "to": "Order", "cardinality": "||--o{", "label": "places"}]
        
    Returns:
        Código Mermaid
    """
    mermaid = [f"---", f"title: {title}", f"---", "erDiagram"]
    
    # Entidades
    for entity in entities:
        name = entity.get("name", "Entity")
        mermaid.append(f"    {name} {{")
        
        for attr in entity.get("attributes", []):
            attr_type = attr.get("type", "string")
            attr_name = attr.get("name", "")
            pk = " PK" if attr.get("pk") else ""
            fk = " FK" if attr.get("fk") else ""
            mermaid.append(f"        {attr_type} {attr_name}{pk}{fk}")
        
        mermaid.append("    }")
    
    mermaid.append("")
    
    # Relacionamentos
    # Cardinalidades: ||--|| (one-to-one), ||--o{ (one-to-many), }o--o{ (many-to-many)
    for rel in relationships:
        from_e = rel.get("from", "")
        to_e = rel.get("to", "")
        card = rel.get("cardinality", "||--o{")
        label = rel.get("label", "relates")
        mermaid.append(f"    {from_e} {card} {to_e} : {label}")
    
    return "\n".join(mermaid)


def generate_state_diagram(
    title: str,
    states: List[str],
    transitions: List[Dict[str, str]]
) -> str:
    """
    Gera um diagrama de estados.
    
    Args:
        title: Título
        states: Lista de estados
        transitions: Transições [{"from": "Idle", "to": "Running", "trigger": "start"}]
        
    Returns:
        Código Mermaid
    """
    mermaid = [f"---", f"title: {title}", f"---", "stateDiagram-v2"]
    
    # Estado inicial
    if states and "start" not in [s.lower() for s in states]:
        mermaid.append(f"    [*] --> {states[0]}")
    
    # Transições
    for trans in transitions:
        from_s = trans.get("from", "")
        to_s = trans.get("to", "")
        trigger = trans.get("trigger", "")
        
        if from_s == "[*]" or to_s == "[*]":
            mermaid.append(f"    {from_s} --> {to_s}")
        elif trigger:
            mermaid.append(f"    {from_s} --> {to_s} : {trigger}")
        else:
            mermaid.append(f"    {from_s} --> {to_s}")
    
    return "\n".join(mermaid)


def analyze_python_structure(file_path: str) -> Dict[str, Any]:
    """
    Analisa estrutura de um arquivo Python para gerar diagrama.
    
    Args:
        file_path: Caminho do arquivo
        
    Returns:
        Dicionário com classes, funções e imports
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        tree = ast.parse(source)
    except Exception as e:
        return {"error": str(e)}
    
    classes = []
    functions = []
    imports = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            cls_info = {
                "name": node.name,
                "attributes": [],
                "methods": [],
                "bases": [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases]
            }
            
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    # Pegar argumentos
                    args = [arg.arg for arg in item.args.args if arg.arg != 'self']
                    method_sig = f"{item.name}({', '.join(args)})"
                    cls_info["methods"].append(method_sig)
                    
                    # Detectar atributos no __init__
                    if item.name == '__init__':
                        for stmt in ast.walk(item):
                            if isinstance(stmt, ast.Assign):
                                for target in stmt.targets:
                                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                                        if target.value.id == 'self':
                                            cls_info["attributes"].append(target.attr)
                
                elif isinstance(item, ast.AnnAssign):
                    if isinstance(item.target, ast.Name):
                        cls_info["attributes"].append(item.target.id)
            
            classes.append(cls_info)
        
        elif isinstance(node, ast.FunctionDef) and not any(
            isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)
        ):
            args = [arg.arg for arg in node.args.args]
            functions.append({
                "name": node.name,
                "args": args
            })
        
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    
    return {
        "file_path": file_path,
        "classes": classes,
        "functions": functions,
        "imports": list(set(imports))
    }


def generate_class_diagram_from_file(file_path: str) -> str:
    """
    Gera diagrama de classes automaticamente de um arquivo Python.
    
    Args:
        file_path: Caminho do arquivo
        
    Returns:
        Código Mermaid do diagrama
    """
    structure = analyze_python_structure(file_path)
    
    if "error" in structure:
        return f"Erro ao analisar arquivo: {structure['error']}"
    
    classes = structure.get("classes", [])
    if not classes:
        return "Nenhuma classe encontrada no arquivo"
    
    # Detectar relacionamentos de herança
    relationships = []
    for cls in classes:
        for base in cls.get("bases", []):
            # Verificar se a classe base está no mesmo arquivo
            base_names = [c["name"] for c in classes]
            if base in base_names:
                relationships.append({
                    "from": cls["name"],
                    "to": base,
                    "type": "inheritance"
                })
    
    return generate_class_diagram(
        title=Path(file_path).stem,
        classes=classes,
        relationships=relationships
    )


def generate_architecture_diagram(
    title: str,
    components: List[Dict[str, Any]],
    flows: List[Dict[str, str]]
) -> str:
    """
    Gera um diagrama de arquitetura.
    
    Args:
        title: Título
        components: Componentes [{"id": "api", "name": "API Gateway", "type": "service"}]
        flows: Fluxos de dados [{"from": "client", "to": "api", "label": "HTTP"}]
        
    Returns:
        Código Mermaid
    """
    mermaid = [f"---", f"title: {title}", f"---", "flowchart LR"]
    
    # Subgraphs por tipo
    component_types = {}
    for comp in components:
        comp_type = comp.get("type", "service")
        if comp_type not in component_types:
            component_types[comp_type] = []
        component_types[comp_type].append(comp)
    
    type_labels = {
        "client": "Clientes",
        "service": "Serviços",
        "database": "Dados",
        "external": "Externos",
        "queue": "Filas"
    }
    
    type_shapes = {
        "client": ("((", "))"),
        "service": ("[", "]"),
        "database": ("[(", ")]"),
        "external": ("{{", "}}"),
        "queue": ("[/", "\\]")
    }
    
    for comp_type, comps in component_types.items():
        label = type_labels.get(comp_type, comp_type.title())
        mermaid.append(f"    subgraph {comp_type}[{label}]")
        
        prefix, suffix = type_shapes.get(comp_type, ("[", "]"))
        for comp in comps:
            comp_id = comp.get("id", "")
            comp_name = comp.get("name", "")
            mermaid.append(f"        {comp_id}{prefix}{comp_name}{suffix}")
        
        mermaid.append("    end")
    
    mermaid.append("")
    
    # Fluxos
    for flow in flows:
        from_id = flow.get("from", "")
        to_id = flow.get("to", "")
        label = flow.get("label", "")
        
        if label:
            mermaid.append(f"    {from_id} -->|{label}| {to_id}")
        else:
            mermaid.append(f"    {from_id} --> {to_id}")
    
    return "\n".join(mermaid)


def save_diagram(
    mermaid_code: str,
    file_path: str,
    format: str = "md"
) -> Dict[str, Any]:
    """
    Salva diagrama Mermaid em arquivo.
    
    Args:
        mermaid_code: Código Mermaid
        file_path: Caminho do arquivo
        format: Formato (md, mmd, html)
        
    Returns:
        Resultado da operação
    """
    try:
        if format == "md":
            content = f"```mermaid\n{mermaid_code}\n```"
        elif format == "html":
            content = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
</head>
<body>
    <div class="mermaid">
{mermaid_code}
    </div>
    <script>mermaid.initialize({{startOnLoad:true}});</script>
</body>
</html>
"""
        else:  # mmd
            content = mermaid_code
        
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "success": True,
            "file_path": file_path,
            "format": format
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
