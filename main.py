# [5] Script principal
#---
import os
from datetime  import datetime

import config as cf

from cf_files_path import(
    _get_base_path,
    _find_report_folder,
    _find_semantic_model_folder,
)

from cf_files_read import(
    _build_model_from_tmdl,
)

from cf_model_extract import(
    _extract_tables,
    _extract_sources,
    _extract_measures,
    _extract_relationships,
)

from cf_layout_extract import (
    _extract_pages,
    _extract_visuals,
)


# Função que configura a documentação
def createDoc(report_path, Model, report_title):
    dt_doc = datetime.now().strftime("%d/%m/%Y")

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

{_extract_pages(report_path)}

## 📊 Mockup
<img src={cf.mkp_img}>

{_extract_tables(Model)}

{_extract_sources(Model)}

{_extract_measures(Model)}

{_extract_visuals(report_path, Model)}

{_extract_relationships(Model)}

## 🚧 Updates

| Version               | Date        | Updates         |
|-----------------------|-------------|-----------------|
| v{cf.proj_version}   | {dt_doc}    | Auto generated |
"""

# Função que realiza a leitura do projeto
def readProject(report_path):
    semantic_model_path = _find_semantic_model_folder(report_path)

    if not semantic_model_path or not os.path.isdir(semantic_model_path):
        raise FileNotFoundError(
            f"SemanticModel not found for report: {os.path.basename(report_path)}"
        )

    Model = _build_model_from_tmdl(semantic_model_path)
    report_title = os.path.basename(report_path).replace(".Report", "")
    readme_path = os.path.join(report_path, "README.md")

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(createDoc(report_path, Model, report_title=report_title))

    return readme_path

# Função que cria a documentação
def main():
    base_path = _get_base_path()
    report_path = _find_report_folder(base_path)
    readme_path = readProject(report_path)

    print("Finished:")
    print(f"- {readme_path}")
            

if __name__ == "__main__":
    main()