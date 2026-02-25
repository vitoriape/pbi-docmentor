# Imports
import os
import json
import zipfile
import shutil
import config as cf
from datetime import datetime

# Paths
DIR = os.path.dirname(os.path.abspath(__file__))
bi_path = DIR
doc_path = DIR


# [1] Configuração dos ficheiros
#---
# Função que extrai os arquivos do projeto
def extractFiles(zip_path, out_dir):
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extract('Report/Layout', out_dir)
        z.extract('DataModelSchema', out_dir)


# Função que abre o JSON do arquivo do projeto para leitura
def loadJSON(actual_path, encoding='utf-16-le'):
    with open(actual_path, 'r', encoding=encoding) as f: 
        return json.load(f)
    

# [2] Extração dos dados | Layout
#---
# Função que extrai a listagem de todas as abas (páginas) do relatório PBI, a partir do arquivo [Layout]
def extractPages(Layout):
    linhas = ["## 📃 Estrutura do Relatório\n"]
    for s in Layout.get("sections", []):
        linhas.append(f"- **{s.get('displayName')}**")
    
    return "\n".join(linhas)


# Função que extrai os visuais usados no relatório PBI, organizando por página e listando cada tipo encontrado
def extractVisuals(Layout):
    linhas = ["## 📈 Layout e Visuais\n"]
    for s in Layout.get("sections", []):
        linhas.append(f"### **{s.get('displayName')}**")

        for v in s.get("visualContainers", []):
            cf_visual = json.loads(v.get("config", "{}"))
            visual_type = cf_visual.get("singleVisual", {}).get("visualType")

            linhas.append(f"- Tipo de visual: `{visual_type}`")
    
    return "\n".join(linhas)


# [3] Extração dos dados | Model
#---
# Função que extrai dados das tabelas do relatório PBI, a partir do arquivo [Model]
def extractTables(Model):
    linhas = [
        "## 🧩 Modelagem de Dados\n",
        "| Tabela | Coluna | Tipo | Calculada |",
        "|-------|--------|------|-----------|"
    ]
    for t in Model.get("model", {}).get("tables", []):
        if t["name"].startswith(("DateTableTemplate", "LocalDateTable")):
            continue

        for c in t.get("columns", []):
            linhas.append(
                f"| {t['name']} | {c['name']} | {c.get('dataType','')} | "
                f"{'Sim' if c.get('type') in ['calculated','calculatedTableColumn'] else 'Não'} |"
            )

    return "\n".join(linhas)


# Função que extrai dados das medidas dax do relatório PBI, a partir do arquivo [Model]
def extractMeasures(Model):
    linhas = [
        "## 🧮 Principais Medidas DAX\n",
        "| Tabela | Medida | Expressão |",
        "|--------|--------|-----------|"
    ]
    for t in Model.get("model", {}).get("tables", []):

        for m in t.get("measures", []):
            expr = m.get("expression", "")

            if isinstance(expr, list):
                expr = " ".join(expr)
            linhas.append(
                f"| {t['name']} | {m['name']} | `{expr}` |"
            )

    return "\n".join(linhas)


# Função que extrai dados das datasources do relatório PBI, a partir do arquivo [Model]
def extractSources(Model):
    linhas = [
        "## ⚙️ Fontes de Dados\n",
        "| Tabela | Tipo | Modo | Fonte |",
        "|--------|------|------|-------|"
    ]
    for t in Model.get("model", {}).get("tables", []):
        if t['name'].startswith(("DateTableTemplate", "LocalDateTable")):
            continue

        for p in t.get("partitions", []):
            src = p.get("source", {})
            expr = src.get("expression", "")

            if isinstance(expr, list):
                expr = " ".join(expr)
            linhas.append(
                f"| {t['name']} | {src.get('type')} | {p.get('mode')} | {expr} |"
            )
    
    return "\n".join(linhas)


# Função que extrai dados dos relacionamentos entre as tabelas no relatório PBI, a partir do arquivo [Model]
def extractRelationships(Model):
    linhas = [
        "## 🔗 Relacionamentos\n",
        "| De | Para | Coluna Origem  | Coluna Destino |",
        "|----|------|----------------|----------------|"
    ]
    for r in Model.get("model", {}).get("relationships", []):
        linhas.append(
            f"| {r['fromTable']} | {r['toTable']} | "
            f"{r.get('fromColumn','')} | {r.get('toColumn','')} |"
        )
    
    return "\n".join(linhas)


# [4] Configuração da documentação
#---
# Função que define o layout do arquivo README
def createDoc(Layout, Model, report_title):
    dt_doc = datetime.now().strftime('%d/%m/%Y')

    return f"""# {report_title}
<img src={cf.bi_icon} width="10%" height="00%" align="right" valign="middle"/>

_{cf.bi_description}_

<div align="center">

![version](https://img.shields.io/badge/version-{cf.proj_version}-red.svg)
![powerbi](https://img.shields.io/badge/PowerBI-{cf.bi_version}-yellow.svg)

</div>

<details>
  <summary>[Open/Close] Table of Contents</summary>

<!--ts-->
- [{report_title}](#)
<!--te-->

</details>

{extractPages(Layout)}

## 📊 Mockup
<img src={cf.mkp_img}>

{extractTables(Model)}

{extractSources(Model)}

{extractMeasures(Model)}

{extractVisuals(Layout)}

{extractRelationships(Model)}

## 🚧 Histórico de Versões

| Versão               | Data        | Alterações         |
|----------------------|-------------|--------------------|
| v{cf.proj_version}   | {dt_doc}    | Geração automática |
"""


# [5] Loop para os arquivos .pbit
def readPBIT(pbit_path, base_dir):
    pbit_filename = os.path.basename(pbit_path)
    stem = os.path.splitext(pbit_filename)[0]

    out_folder = os.path.join(base_dir, stem)
    os.makedirs(out_folder, exist_ok=True)

    work_dir = out_folder # Cria uma temp folder dentro da pasta

    # Move o arquivo .pdbit para a pasta criada
    pbit_in_folder = os.path.join(out_folder, pbit_filename)
    if os.path.abspath(pbit_path) != os.path.abspath(pbit_in_folder):
        shutil.move(pbit_path, pbit_in_folder)

    # Cria uma cópia do .zip
    zip_path = os.path.join(out_folder, f"{stem}.zip")
    if not os.path.exists(zip_path):
        shutil.copy2(pbit_in_folder, zip_path)

    # Extrai os arquivos necessários
    extractFiles(zip_path, work_dir)

    report_dir = os.path.join(out_folder, "Report")
    os.makedirs(report_dir, exist_ok=True)

    model_original_path = os.path.join(out_folder, "DataModelSchema")
    model_new_path = os.path.join(report_dir, "DataModelSchema")

    if os.path.exists(model_original_path):
        shutil.move(model_original_path, model_new_path)


    layout_path = os.path.join(report_dir, "Layout")
    model_path = model_new_path

    Layout = loadJSON(layout_path)
    Model = loadJSON(model_path)

    # Escreve o README dentro da pasta de cada projeto
    readme_path = os.path.join(out_folder, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(createDoc(Layout, Model, report_title=stem))

    # Remove os arquivos temporários
    if os.path.exists(zip_path):
        os.remove(zip_path)

    return readme_path


# [6] Criação da documentação
def main():
    base_dir = DIR

    # Criar um array com os arquivos .pbit
    pbit_files = [
        os.path.join(base_dir, f)
        for f in os.listdir(base_dir)
        if f.lower().endswith(".pbit") and os.path.isfile(os.path.join(base_dir, f))
    ]

    # Error log quando não encontra arquivos da extensão necessária
    if not pbit_files:
        raise FileNotFoundError(f"No .pbit files found in: {base_dir}")
    
    # Loop com todos os arquivos .pbit
    created = []
    for pbit_path in pbit_files:
        created.append(readPBIT(pbit_path, base_dir))

    print("Finished: ")
    for p in created:
        print(f"- {p}")

if __name__ == "__main__":
    main()