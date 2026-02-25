# PBI Docmentor<img src="https://snipboard.io/lGHeSi.jpg" width="10%" height="00%" align="right" valign="middle"/>
A Python automation that creates documentation for a Power BI dashboard by extracting data from its `.pbit` file and generating a README that includes the report structure, layout and visuals, data model (tables, columns, and data types), DAX measures, data sources and relationships. 

<div align="center">

![version](https://img.shields.io/badge/version-1.0-red.svg)
![status](https://img.shields.io/badge/status-stable-006400.svg)
![python](https://img.shields.io/badge/Python-3.12.10-navy.svg)
![PowerBI](https://img.shields.io/badge/PowerBI-Any-yellow.svg)

</div>

<details>
    <summary>[Open/Close] Table of Contents</summary>

- [PBI Docmentor](#pbi-docmentor)
  - [📄 Disclaimer](#-disclaimer)
  - [💡 Technologies](#-technologies)
  - [🚀 Build and Run](#-build-and-run)
  - [⚙️ General Settings](#️-general-settings)
    - [📊 Set on PowerBI](#-set-on-powerbi)
    - [▶️ Set for README](#️-set-for-readme)
  - [📁 Expected Architecture](#-expected-architecture)
  - [🚧 Versions](#-versions)

</details>

---

## 📄 Disclaimer
This project is a fork of [Julia Azevedo's](https://github.com/data-ju/Power_BI_Documentation/commits?author=data-ju) [Power_BI_Documentation](https://github.com/data-ju/Power_BI_Documentation/tree/main) project. It is a Python-only implementation, with no AI components or `.docx` files.

## 💡 Technologies
- Python (env or local)
- PowerBI Desktop

## 🚀 Build and Run
1. Clone this repository
2. Review `requirements.py` and install the required dependencies
3. Follow the PowerBI [setup steps](#-set-on-powerbi) to generate the PowerBI files
4. Follow the project [setup steps](#-set-on-project) to customize your README file
5. Check the expected [final project architecture](#️-final-architecture)
6. Run `main.py`
7. Note that the table of contents in the README file only loads all sections after the file is saved
  
## ⚙️ General Settings
### 📊 Set on PowerBI
1. Open your `.pbix` file on PowerBI Desktop
2. Go to File > Export > PowerBI template
3. Save `.pbit` file in this project folder

### ▶️ Set for README
1. Open `config.py` and update the variable values according to your project

| Variable       | Description                         |
|----------------|-------------------------------------|
| bi_name        | Heading of the README               |
| bi_icon        | A JPG icon that follows the heading |
| bi_description | Description of your BI project      |
| proj_version   | Version of your BI project          |
| bi_version     | Engine version of PowerBI           |
| mkp_img        | A JPG mockup of your BI project     |

## 📁 Expected Architecture
<pre><code>/pbi-docmentor
├── {your-report}.pbit
├── config.py
├── main.py
├── README.md
├── requirements.py
</code></pre>

>---

## 🚧 Versions

<details>
  <summary>[See/Hide] Version: 1.0 </summary>

  ![status](https://img.shields.io/badge/status-published-black.svg)
  ![date](https://img.shields.io/badge/date-2026/02/25-black.svg)

Fork project and adapt its features
</details>