# PBI Docmentor<img src="https://snipboard.io/lGHeSi.jpg" width="10%" height="00%" align="right" valign="middle"/>
A Python automation that creates documentation for a Power BI dashboard by extracting metadata from the Power BI Project structure generated through Git integration, producing a README with report structure, layout and visuals, semantic model information, DAX measures, data sources, and relationships.

<div align="center">

![version](https://img.shields.io/badge/version-1.0-red.svg)
![status](https://img.shields.io/badge/status-stable-006400.svg)
![python](https://img.shields.io/badge/Python-3.12.10-navy.svg)
![Power BI](https://img.shields.io/badge/Power_BI-Git_Integration-yellow.svg)

</div>

<details>
    <summary>[Open/Close] Table of Contents</summary>

- [PBI Docmentor](#pbi-docmentor)
  - [📄 Disclaimer](#-disclaimer)
  - [💡 Technologies](#-technologies)
  - [🚀 Build and Run](#-build-and-run)
  - [⚙️ General Settings](#️-general-settings)
    - [📊 Set in Power BI](#-set-in-power-bi)
    - [▶️ Set for README](#️-set-for-readme)
  - [📁 Expected Architecture](#-expected-architecture)
    - [Documentation Project](#documentation-project)
    - [Power BI Project Folder](#power-bi-project-folder)
  - [🚧 Versions](#-versions)
    - [Standard](#standard)
    - [DataOps](#dataops)

</details>

---

## 📄 Disclaimer
This project is a fork of [Julia Azevedo's](https://github.com/data-ju/Power_BI_Documentation/commits?author=data-ju) [Power_BI_Documentation](https://github.com/data-ju/Power_BI_Documentation/tree/main), redesigned as a Python-only implementation with no AI components or `.docx` generation. This version works with Power BI files exported through **Git integration / Power BI Project format**, using JSON-based project metadata instead of `.pbit` files.

## 💡 Technologies
- Python
- Power BI Git Integration
- Power BI Project structure
- JSON metadata
- TMDL semantic model files

## 🚀 Build and Run
1. Clone this repository
2. This version currently does not require external Python dependencies
3. Follow the Power BI [setup steps](#-set-in-power-bi) to prepare the project structure
4. Run `main.py`
5. The script will ask you to select the main project folder
6. The selected folder must contain:
   - exactly one `.Report` folder
   - exactly one `.SemanticModel` folder
7. The generated `README.md` file will be created for the selected report
8. Note that the table of contents in the generated README may only fully update after the file is saved

## ⚙️ General Settings
### 📊 Set in Power BI
1. Make sure the latest version of your Power BI project is available through **Source control** / **Git integration**
2. Clone or export the repository containing the Power BI project structure
3. Confirm that the folder selected in the script contains:
   - exactly one `.Report` folder
   - exactly one `.SemanticModel` folder
4. Run the script and select that folder when prompted

### ▶️ Set for README
1. Open `config.py` and update the variable values according to your project

| Variable       | Description                         |
|----------------|-------------------------------------|
| bi_icon        | A JPG icon that follows the heading |
| bi_description | Description of your BI project      |
| proj_version   | Version of your BI project          |
| bi_version     | Engine version of Power BI           |
| mkp_img        | A JPG mockup of your BI project     |

## 📁 Expected Architecture

### Documentation Project
<pre><code>/pbi-docmentor
├── cf_files_path.py
├── cf_files_read.py
├── cf_layout_extract.py
├── cf_model_extract.py
├── config.py
├── main.py
├── README.md
</code></pre>

### Power BI Project Folder
<pre><code>/{your-project-folder-on-github}
├── {your-report}.Report/
└── {your-model}.SemanticModel/
</code></pre>

The script will ask the user to select the Power BI project folder during execution. The selected folder must contain exactly one `.Report` and `.SemanticModel` folder. **If more than one folder of the same type is found, the script will return a validation error.**

> The generated `README.md` file will be created inside the `.Report` folder, not in the root project folder and not in the script directory.

>---

## 🚧 Versions
### Standard
<details>
  <summary>[See/Hide] Standard Version: 1.0 </summary>

  ![status](https://img.shields.io/badge/status-published-black.svg)
  ![date](https://img.shields.io/badge/date-2026/02/25-black.svg)

Fork project and adapt its features
</details>

### DataOps
<details>
  <summary>[See/Hide] DataOps Version: 1.0 </summary>

  ![status](https://img.shields.io/badge/status-published-black.svg)
  ![date](https://img.shields.io/badge/date-2026/03/30-black.svg)

Branch structured around DataOps-inspired principles, improving modularity and making reviews easier
</details>