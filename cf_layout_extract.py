# [3] Extração dos dados (Layout)
#---
import os
from cf_files_path import _load_json, _clean_literal, _dedupe


# Função auxiliar que extrai uma lista com as páginas do relatório
def _extract_pages(report_path):
    pages_index_path = os.path.join(report_path, "definition", "pages", "pages.json")
    pages_index = _load_json(pages_index_path, default={})
    
    linhas = ["## 📃 Report Structure\n"]
    page_order = pages_index.get("pageOrder", [])
    
    for page_id in page_order:
        page_json_path = os.path.join(report_path, "definition", "pages", page_id, "page.json")
        page_json = _load_json(page_json_path, default={})
        display_name = page_json.get("displayName") or page_json.get("name") or page_id
        linhas.append(f"- **{display_name}**")
        
    return "\n".join(linhas)

# Função auxiliar que extrai a referência de campo de um visual
def _extract_field_ref(field_obj):
    if not isinstance(field_obj, dict):
        return None
    
    # Referência de medida
    if "Measure" in field_obj:
        measure = field_obj["Measure"]
        entity = measure.get("Expression", {}).get("SourceRef", {}).get("Entity")
        prop = measure.get("Property")
        # Só retorna uma referência válida quando tabela e campo existem
        if entity and prop:
            return {
                "kind": "measure",
                "reference": f"{entity}[{prop}]",
                "table": entity,
                "name": prop
            }
            
    # Referência de coluna
    if "Column" in field_obj:
        column = field_obj["Column"]
        entity = column.get("Expression", {}).get("SourceRef", {}).get("Entity")
        prop = column.get("Property")
        # Só retorna uma referência válida quando tabela e campo existem
        if entity and prop:
            return {
                "kind": "column",
                "reference": f"{entity}[{prop}]",
                "table": entity,
                "name": prop
            }

    # Referência de agregação
    if "Aggregation" in field_obj:
        agg = field_obj["Aggregation"]
        func = agg.get("Function", "")
        col = agg.get("Expression", {}).get("Column", {})
        entity = col.get("Expression", {}).get("SourceRef", {}).get("Entity")
        prop = col.get("Property")
        # Só retorna uma referência válida quando tabela e campo existem
        if entity and prop:
            return {
                "kind": "aggregation",
                "reference": f"{func}({entity}[{prop}])" if func else f"{entity}[{prop}]",
                "table": entity,
                "name": prop
            }

    return None

# Função auxiliar que converte os tipos de visual do PowerBI em legendas mais amigáveis (PT_BR)
def _normalize_visual_type(visual_type):
    visual_map = {
        "donutChart": "gráfico de rosca",
        "pieChart": "gráfico de pizza",
        "lineChart": "gráfico de linha",
        "clusteredColumnChart": "gráfico de colunas agrupadas",
        "stackedColumnChart": "gráfico de colunas empilhadas",
        "clusteredBarChart": "gráfico de barras agrupadas",
        "stackedBarChart": "gráfico de barras empilhadas",
        "tableEx": "tabela",
        "pivotTable": "matriz",
        "card": "cartão",
        "cardVisual": "cartão",
        "multiRowCard": "cartão multilinha",
        "slicer": "segmentação",
        "treemap": "treemap",
        "scatterChart": "gráfico de dispersão",
        "areaChart": "gráfico de área",
        "filledMap": "mapa preenchido",
        "map": "mapa",
        "azureMap": "mapa",
        "waterfallChart": "gráfico de cascata",
        "gauge": "medidor",
        "kpi": "kpi",
        "image": "imagem",
        "textbox": "caixa de texto",
        "shape": "forma"
    }
    return visual_map.get(visual_type, visual_type or "unknow") # Se não encontra, retorna unknow

# Função auxiliar que extrai o título de um visual
def _get_visual_title(visual_json, fallback_name):
    try:
        title_blocks = (
            visual_json.get("visual", {})
            .get("visualContainerObjects", {})
            .get("title", [])
        )
        
        for block in title_blocks:
            props = block.get("properties", {})
            show = props.get("show", {}).get("expr", {}).get("Literal", {}).get("Value")
            text = props.get("text", {}).get("expr", {}).get("Literal", {}).get("Value")
            
            if text:
                return _clean_literal(text)
            
    except Exception:
        pass
    
    return fallback_name

# Função auxiliar que extrai o tipo de um visual
def _get_visual_type(visual_json):
    return (
        visual_json.get("visual", {}).get("visualType")
        or visual_json.get("visualType")
        or "unknow"
    )
    
# Função auxiliar que constrói um catálogo com todas as medidas do modelo semântico
def _build_measure_catalog(Model):
    catalog = {}
    
    for t in Model.get("model", {}).get("tables", []):
        table_name = t.get("name", "")
        
        for m in t.get("measures", []):
            reference = f"{table_name}[{m.get('name', '')}]"
            catalog[reference] = {
                "table": table_name,
                "name": m.get("name", ""),
                "expression": m.get("expression", ""),
                "description": m.get("description", ""),
                "displayFolder": m.get("displayFolder", "")
            }
            
    return catalog

# Função auxiliar que constrói um catálogo com todas as colunas do modelo semântico
def _build_column_catalog(Model):
    catalog = {}
    
    for t in Model.get("model", {}).get("tables", []):
        table_name = t.get("name", "")
        # Desconsidera tabela auto-geradas
        if table_name.startswith(("DateTableTemplate", "LocalDateTable")):
            continue
        
        for c in t.get("columns", []):
            reference = f"{table_name}[{c.get('name', '')}]"
            catalog[reference] = {
                "table": table_name,
                "name": c.get("name", ""),
                "dataType": c.get("dataType", ""),
                "description": c.get("description", "")
            }
            
    return catalog

# Função auxiliar que adiciona os metadados do modelo semântico a uma referência vinculada ao visual
def _enrich_binding(ref_data, measure_catalog, column_catalog):
    item = dict(ref_data)
    ref = item.get("reference", "")
    
    # Linka os metadados da medida
    if ref in measure_catalog:
        meta = measure_catalog[ref]
        item["kind"] = "measure"
        item["formula"] = meta.get("expression", "")
        item["description"] = meta.get("description", "")
        
        return item
    
    # Linka os metadados da coluna
    if ref in column_catalog:
        meta = column_catalog[ref]
        item["kind"] = "column"
        item["description"] = meta.get("description", "")
        item["dataType"] = meta.get("dataType", "")
        
        return item
    
    return item # Retorna o binding original quando nenhum catálog pode ser vinculado
    
# Função auxiliar que realiza um parser nos campos vinculados
def _parser_visual_bindings(visual_json, measure_catalog, column_catalog):
    bindings = []
    query_status = (
        visual_json.get("visual", {})
        .get("query", {})
        .get("queryState", {})
    )
    
    for role_name, role_data in query_status.items():
        if not isinstance(role_data, dict):
            continue
        
        projections = role_data.get("projections", [])
        if not isinstance(projections, list):
            continue
        
        for proj in projections:
            field = proj.get("field", {})
            ref_data = _extract_field_ref(field)
            # Pula projeções sem referência válida de campo
            if not ref_data:
                continue
            
            ref_data["role"] = role_name
            ref_data = _enrich_binding(ref_data, measure_catalog, column_catalog)
            bindings.append(ref_data)
            
    return _dedupe(bindings)

# Função auxiliar que extrai visuais e dados vinculados
def _extract_visuals(report_path, Model):
    measure_catalog = _build_measure_catalog(Model)
    column_catalog = _build_column_catalog(Model)
    
    pages_index_path = os.path.join(report_path, "definition", "pages", "pages.json")
    pages_index = _load_json(pages_index_path, default={})
    page_order = pages_index.get("pageOrder", [])
    
    linhas = ["## 📈 Layout and Visuals\n"]
    
    for page_id in page_order:
        page_json_path = os.path.join(report_path, "definition", "pages", page_id, "page.json")
        page_json = _load_json(page_json_path, default={})
        page_name = page_json.get("displayName") or page_json.get("name") or page_id
        
        linhas.append(f"### **{page_name}**")
        visuals_dir = os.path.join(report_path, "definition", "pages", page_id, "visuals")
        
        # Se a página não tem diretório de visuais, mantém o cabeçalho e continua
        if not os.path.isdir(visuals_dir):
            linhas.append("")
            continue
        
        visuals_folder = sorted(
            [
                os.path.join(visuals_dir, v)
                for v in os.listdir(visuals_dir)
                if os.path.isdir(os.path.join(visuals_dir, v))
            ]
        )
        
        for visual_folder in visuals_folder:
            visual_json_path = os.path.join(visual_folder, "visual.json")
            # Pula diretórios sem definição de visual
            if not os.path.isfile(visual_json_path):
                continue
            
            visual_json = _load_json(visual_json_path, default={})
            visual_id = visual_json.get("name") or os.path.basename(visual_folder)
            visual_title = _get_visual_title(visual_json, visual_id)
            visual_type = _normalize_visual_type(_get_visual_type(visual_json))
            
            bindings = _parser_visual_bindings(visual_json, measure_catalog, column_catalog)
            # Pula visuais sem vinculações detectáveis
            if not bindings:
                continue
            
            linhas.append(f"#### **{visual_title}")
            linhas.append(f"- Types: `{visual_type}`")
            
            for b in bindings:
                linhas.append(f"- {b.get('role', 'Campo')} - `{b.get('reference', '')}`")
            linhas.append("")
            
            added_measures = set()
            for b in bindings:
                if b.get("kind") != "measure":
                    continue
                
                ref = b.get("reference", "")
                # Evita repetição de medidas
                if ref in added_measures:
                    continue
                added_measures.add(ref)
                
                linhas.append(f"**{b.get('name', '')}**")
                if b.get("formula"):
                    linhas.append(f"- Formula: `{b.get('formula', '')}`")
                if b.get("description"):
                    linhas.append(f"- Description: `{b.get('description', '')}`")
                linhas.append("")
                
            added_columns = set()
            for b in bindings:
                if b.get("kind") not in ["column", "aggregation"]:
                    continue
                
                ref = b.get("reference", "")
                # Evita repetição de colunas/agregação
                if ref in added_columns:
                    continue
                added_columns.add(ref)
                
                linhas.append(f"**{b.get('name', '')}**")
                linhas.append(f"- Table Reference: `{ref}`")
                if b.get("description"):
                    linhas.append(f"- Description: `{b.get('description', '')}`")
                linhas.append("")
                
    return "\n".join(linhas)