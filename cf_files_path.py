# [1] Funções de configuração dos ficheiros
#---
import os
import json
import re
import tkinter as tk
from tkinter import filedialog, messagebox

# Paths
DIR = os.path.dirname(os.path.abspath(__file__))
bi_path = DIR
doc_path = DIR


# Função auxiliar que solicita ao usuário o caminho para a pasta mãe do projeto
def _get_base_path():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    
    messagebox.showinfo(
        "Select project folder",
        "Select the main folder that contains exactly one .Report and .SemanticModel folder each"
    )
    
    base_path = filedialog.askdirectory(
        title="Project Folder",
        initialdir=DIR
    )
    
    root.destroy()
    
    if not base_path:
        raise FileNotFoundError("Folder not found")
    
    if not os.path.isdir(base_path):
        raise FileNotFoundError("Not a folder")
    
    return os.path.abspath(base_path)
    
    
# Função auxiliar que lê JSON e retorna seu conteúdo
def _load_json(actual_path, encoding="utf-8", default=None):
    if not os.path.isfile(actual_path):
        return {} if default is None else default
    
    with open(actual_path, "r", encoding=encoding) as f:
        return json.load(f)
    
# Função auxiliar que retorna texto em arquivo
def _read_text(path, encoding="utf-8"):
    with open(path, "r", encoding=encoding) as f:
        return f.read()
    
# Função auxiliar que remove single quotes de uma strings
def _clean_literal(value):
    if not isinstance(value, str):
        return value
    value = value.strip()
    
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    return value

# Função auxiliar que normaliza espaços em branco em strings
def _normalize_spaces(text):
    return re.sub(r"\s+", " ", text).strip()

# Função auxiliar que remove itens duplicados de uma lista, preservando sua ordem
def _dedupe(items):
    seen = set()
    out = []
    
    for item in items:
        if isinstance(item, dict):
            key = json.dumps(item, ensure_ascii=False, sort_keys=True)
        else:
            key = str(item)
            
        if key not in seen:
            seen.add(key)
            out.append(item)
            
    return out

# Função auxiliar que busca todos os diretórios com ".Report"
def _find_report_folders(base_path):
    reports = []
    
    for name in sorted(os.listdir(base_path)):
        full = os.path.join(base_path, name)
        
        if os.path.isdir(full) and name.endswith(".Report"):
            reports.append(full)
            
    return reports

# Função auxiliar que identifica o modelo semântico do relatório e localiza seu path
def _find_semantic_model_folder(report_path):
    definition_pbir = os.path.join(report_path, "definition.pbir")
    
    if not os.path.isfile(definition_pbir):
        return None
    
    pbir = _load_json(definition_pbir, default={})
    rel_path = (
        pbir.get("datasetReference", {})
        .get("byPath", {})
        .get("path")
    )
    
    if not rel_path:
        return None
    
    rel_path = rel_path.replace("/", os.sep).replace("\\", os.sep)
    model_path = os.path.abspath(os.path.join(report_path, rel_path))
    
    if os.path.isdir(model_path):
        return model_path
    
    return None

# Funções auxiliares para localizar os arquivos do projeto
def _find_folders_by_suffix(base_path, suffix):
    found = []

    for name in sorted(os.listdir(base_path)):
        full = os.path.join(base_path, name)

        if os.path.isdir(full) and name.endswith(suffix):
            found.append(full)

    return found


def _validate_project_folder(base_path):
    report_folders = _find_folders_by_suffix(base_path, ".Report")
    semantic_folders = _find_folders_by_suffix(base_path, ".SemanticModel")

    if not report_folders:
        raise FileNotFoundError(
            f"No .Report folder found in: {base_path}"
        )

    if not semantic_folders:
        raise FileNotFoundError(
            f"No .SemanticModel folder found in: {base_path}"
        )

    if len(report_folders) > 1:
        names = ", ".join(os.path.basename(p) for p in report_folders)
        raise FileExistsError(
            f"More than one .Report folder was found in: {base_path}. "
            f"Expected exactly one .Report folder. Found: {names}"
        )

    if len(semantic_folders) > 1:
        names = ", ".join(os.path.basename(p) for p in semantic_folders)
        raise FileExistsError(
            f"More than one .SemanticModel folder was found in: {base_path}. "
            f"Expected exactly one .SemanticModel folder. Found: {names}"
        )

    return report_folders[0], semantic_folders[0]


def _find_report_folder(base_path):
    report_path, _ = _validate_project_folder(base_path)
    return report_path