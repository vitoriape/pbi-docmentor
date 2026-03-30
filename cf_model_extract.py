# [4] Extração dos dados (Modelo)
#---
import os
from cf_files_path import _normalize_spaces


# Função auxiliar que extrai os dados das tabelas do report, ignorando tabelas automáticas
def _extract_tables(Model):
    linhas = [
        "## 🧩 Data Modeling\n",
        "| Table | Column | Type | Calculated |",
        "|-------|--------|------|------------|"
    ]
    
    for t in Model.get("model", {}).get("tables", []):
        if t["name"].startswith(("DateTableTemplate", "LocalDateTable")):
            continue
        
        for c in t.get("columns", []):
            linhas.append(
                f"| {t['name']} | {c['name']} | {c.get('dataType','')} | "
                f"{'Sim' if c.get('type') in ['calculated','calculatedTableColumn'] or c.get('expression') else 'Não'} |"
            )
            
    return "\n".join(linhas)

# Função auxiliar que extrai os dados das medidas DAX criaads no report
def _extract_measures(Model):
    linhas = [
        "## 🧮 Main DAX Measures\n",
        "| Table | Measure | Expression |",
        "|-------|---------|------------|"
    ]
    
    for t in Model.get("model", {}).get("tables", []):
        for m in t.get("measures", []):
            expr = m.get("expression", "")
            expr = _normalize_spaces(expr)
            
            linhas.append(
                f"| {t['name']} | {m['name']} | `{expr}` |"
            )
            
    return "\n".join(linhas)

# Função auxiliar que extrai os dados das fontes de dados do report
def _extract_sources(Model):
    linhas = [
        "## ⚙️ Datasources\n",
        "| Table | Type | Mode | Source |",
        "|-------|-----|-----|-------|"
    ]

    for t in Model.get("model", {}).get("tables", []):
        if t["name"].startswith(("DateTableTemplate", "LocalDateTable")):
            continue

        for p in t.get("partitions", []):
            expr = _normalize_spaces(p.get("expression", ""))

            linhas.append(
                f"| {t['name']} | {p.get('sourceType','')} | {p.get('mode','')} | {expr} |"
            )

    return "\n".join(linhas)

# Função auxiliar que extrai os dados dos relacionamentos criados entre as tabelas no report
def _extract_relationships(Model):
    linhas = [
        "## 🔗 Relationships\n",
        "| From | To | Source Column  | Target Column |",
        "|------|----|----------------|---------------|"
    ]

    for r in Model.get("model", {}).get("relationships", []):
        linhas.append(
            f"| {r.get('fromTable','')} | {r.get('toTable','')} | "
            f"{r.get('fromColumn','')} | {r.get('toColumn','')} |"
        )

    return "\n".join(linhas)