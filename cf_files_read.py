# [2] Leitura do modelo semântico (TMDL)
#---
import os
import config as cf

from cf_files_path import _read_text, _clean_literal


# Função auxiliar que obtém o path da pasta com o modelo semântico
def _get_definition_dir(semantic_model_path):
    return os.path.join(semantic_model_path, "definition")

# Função auxiliar que retorna um array com todas as tabelas .tmdl do modelo semântico
def _get_tmdl_table_files(semantic_model_path):
    tables_dir = os.path.join(_get_definition_dir(semantic_model_path), "tables")
    
    # Retorna uma lista vazia caso não encontre um diretório com as tabelas
    if not os.path.isdir(tables_dir):
        return []
    
    files = []
    for name in sorted(os.listdir(tables_dir)):
        if name.lower().endswith(".tmdl"):
            files.append(os.path.join(tables_dir, name))

    return files

# Função auxiliar que converte texto bruto em tuplas identadas
def _get_indented_lines(text):
    lines = []
    
    for raw in text.splitlines():
        expanded = raw.replace("\t", "    ")
        indent = len(expanded) - len(expanded.lstrip(" "))
        level = indent // 4
        content = expanded.strip()
        lines.append((level, content, raw))
    
    return lines

# Função auxiliar que realiza um parser na tabela TMDL
def _parse_tmdl_table(table_file):
    text = _read_text(table_file)
    lines = _get_indented_lines(text)
    
    table_name = None
    columns = []
    measures = []
    partitions = []
    
    i = 0
    while i < len(lines):
        level, content, _ = lines[i]
        
        # Detecta a declaração da tabela no root level
        if level == 0 and content.startswith("table "):
            table_name = content[len("table "):].strip()
            i += 1
            continue
        
        # Localiza o bloco de coluna dentro da tabela
        if level == 1 and content.startswith("column "):
            header = content[len("column "):].strip()
            
            if "=" in header:
                col_name, col_expr = header.split("=", 1)
                col_name = col_name.strip().strip("'")
                col_expr = col_expr.strip()
            else:
                col_name = header.strip().strip("'")
                col_expr = ""
                
            col = {
                "name": col_name,
                "expression": col_expr,
                "dataType": "",
                "description": "",
                "type": "calculated" if col_expr else ""
            }
            
            j = i + 1
            while j < len(lines):
                next_level, next_content, _ = lines[j]
                
                # Para quando sai do bloco atual
                if next_level <= 1:
                    break
                
                # Lê a coluna [dataType]
                if next_level == 2 and next_content.startswith("dataType:"):
                    col["dataType"] = next_content.split(":", 1)[1].strip()
                    
                # Lê a coluna [description]
                elif next_level == 2 and next_content.startswith("description:"):
                    col["description"] = _clean_literal(next_content.split(":", 1)[1].strip())
                    
                # Usa a coluna [sourceColumn] no lugar de [expression] caso ainda não localize [expression]
                elif next_level == 2 and next_content.startswith("sourceColumn:"):
                    if not col["expression"]:
                        col["expression"] = next_content.split(":", 1)[1].strip()
                        
                j += 1
                
            columns.append(col)
            i = j
            continue
        
        # Localiza o bloco de medidas dentro da tabela
        if level == 1 and content.startswith("measure "):
            header = content[len("measure "):].strip()
            
            # Condicional caso o cabeçalho da medida contenha "="
            if "=" in header:
                measure_name, first_expr = header.split("=", 1)
                measure_name = measure_name.strip().strip("'")
                first_expr = first_expr.strip()
            else:
                measure_name = header.strip().strip("'")
                first_expr = ""
                
            expr_lines = []
            if first_expr:
                expr_lines.append(first_expr)
                
            measure = {
                "name": measure_name,
                "expression": "",
                "description": "",
                "displayFolder": ""
            }
            
            j = i + 1
            while j < len(lines):
                next_level, next_content, _ = lines[j]
                
                # Para quando sai do bloco atual
                if next_level <= 1:
                    break
                
                # Lê os metadados do diretório [displayFolder]
                if next_level == 2 and next_content.startswith("displayFolder:"):
                    measure["displayFolder"] = _clean_literal(next_content.split(":", 1)[1].strip())
                # Lê os metadados do diretório [description]
                elif next_level == 2 and next_content.startswith("description:"):
                    measure["description"] = _clean_literal(next_content.split(":", 1)[1].strip())
                # Coleta tuplas enquanto pula metadados já catalogados
                elif next_level >= 2:
                    if not(
                        next_level == 2 and (
                            next_content.startswith("formatString:")
                            or next_content.startswith("lineageTag:")
                            or next_content.startswith("displayFolder:")
                            or next_content.startswith("description:")
                            or next_content.startswith("dataType:")
                            or next_content.startswith("summarizeBy:")
                            or next_content.startswith("sourceColumn:")
                            or next_content.startswith("annotation ")
                            or next_content.startswith("changedProperty ")
                            or next_content.startswith("extendedProperty ")
                        )
                    ):
                        expr_lines.append(next_content)
                        
                j += 1
                
            expr = "\n".join(expr_lines).strip()
            expr = expr.replace("```", "").strip()
            
            measure["expression"] = expr
            measures.append(measure)
            i = j
            continue
        
        # Localiza o bloco de partição dentro da tabela
        if level == 1 and content.startswith("partition "):
            header = content[len("partition "):].strip()
            part_name = header.split("=", 1)[0].strip()
            part_type = ""
            
            # Se o cabeçalho da partição contém "=", armazena o tipo
            if "=" in header:
                part_type = header.split("=", 1)[1].strip()
                
            partition = {
                "name": part_name,
                "mode": "",
                "sourceType": part_type,
                "expression": ""
            }
            
            expr_lines = []
            j = i + 1
            
            while j < len(lines):
                next_level, next_content, _ = lines[j]
                
                # Para quando sai do bloco atual
                if next_level <= 1:
                    break
                
                # Lê o modo de partição
                if next_level == 2 and next_content.startswith("mode:"):
                    partition["mode"] = next_content.split(":", 1)[1].strip()
                # Lê a primeira linha da source
                elif next_level == 2 and next_content.startswith("source ="):
                    expr_lines.append(next_content.split("=", 1)[1].strip())
                # Lê registros alinhados como parte da expressão
                elif next_level >= 3:
                    expr_lines.append(next_content)
                    
                j += 1
                
            partition["expression"] = "\n".join(expr_lines).strip()
            partitions.append(partition)
            i = j
            continue
            
        i += 1 # Pula registros não relacionados/não suportados
        
    return {
        "name": table_name or os.path.splitext(os.path.basename(table_file))[0],
        "columns": columns,
        "measures": measures,
        "partitions": partitions
    }
        
# Função auxiliar que constroe a estrutura do modelo semântico a partir dos arquivos TMDL
def _build_model_from_tmdl(semantic_model_path):
    model = {"model": {"tables": [], "relationships": []}}
    
    for table_file in _get_tmdl_table_files(semantic_model_path):
        table_data = _parse_tmdl_table(table_file)
        model["model"]["tables"].append(table_data)
        
    relationships_file = os.path.join(_get_definition_dir(semantic_model_path), "relationships.tmdl")
    
    # Se o diretório [relationships] existe, realiza um parser e agrega ao modelo
    if os.path.isfile(relationships_file):
        model["model"]["relationships"] = _parse_relationships_tmdl(relationships_file)
        
    return model

# Função auxiliar que realiza um parser em [relationships] - no arquivo TMDL
def _parse_relationships_tmdl(relationships_file):
    text = _read_text(relationships_file)
    lines = _get_indented_lines(text)
    
    relationships = []
    current = None
    
    for level, content, _ in lines:
        if level == 0 and content.startswith("relationship "):
            if current:
                relationships.append(current)
            current = {
                "name": content[len("relationship "):].strip(),
                "fromTable": "",
                "toTable": "",
                "fromColumn": "",
                "toColumn": "",
                "crossFilteringBehavior": "",
                "fromCardinality": "",
                "toCardinality": ""
            }
            continue
        
        # Ignora registros até que o bloco [relationship] comece
        if not current:
            continue
        
        # Lê a tabela e coluna de origem
        if level == 1 and content.startswith("fromColumn:"):
            value = content.split(":", 1)[1].strip()
            # Realiza um split apenas quando tabela e coluna vem como table.column
            if "." in value:
                t, c = value.split(".", 1)
                current["fromTable"] = t.strip()
                current["fromColumn"] = c.strip()
        # lê a tabela e coluna alvo
        elif level == 1 and content.startswith("toColumn:"):
            value = content.split(":", 1)[1].strip()
            # Realiza um split apenas quando tabela e coluna vem como table.column
            if "." in value:
                t, c = value.split(".", 1)
                current["toTable"] = t.strip()
                current["toColumn"] = c.strip()
        # Lê as configurações de cross-filtering
        elif level == 1 and content.startswith("crossFilteringBehavior:"):
            current["crossFilteringBehavior"] = content.split(":", 1)[1].strip()
        # Lê as configurações de cardinalidade (origem)
        elif level == 1 and content.startswith("fromCardinality:"):
            current["fromCardinality"] = content.split(":", 1)[1].strip()
        # Lê as configurações de cardinalidade (alvo)
        elif level == 1 and content.startswith("toCardinality:"):
            current["toCardinality"] = content.split(":", 1)[1].strip()
        
    # Agrega o último relacionamento ao final do loop
    if current:
        relationships.append(current)
        
    return relationships