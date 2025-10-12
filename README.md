![Preview](assets/preview1.png)

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


**Critiplot** is an open-source Python package for **visualizing risk-of-bias (RoB) assessments** across multiple evidence synthesis tools:

* **Newcastle-Ottawa Scale (NOS)**
* **JBI Critical Appraisal Checklists** (Case Report / Case Series)
* **GRADE certainty of evidence**
* **ROBIS for systematic reviews**

* It produces **publication-ready traffic-light plots** and **stacked bar charts** for summarizing study quality.
* **Python Package**: https://pypi.org/project/critiplot/1.0.1/
---

## 📥 Installation

```bash
# Clone repository
git clone https://github.com/aurumz-rgb/Critiplot-main.git
cd Critiplot-Package

# Install requirements
pip install -r requirements.txt

# Install package locally
pip install .
```

> Requires **Python 3.11**, **Matplotlib**, **Seaborn**, and **Pandas**.

---

## ⚡ Usage

Import the plotting functions from the package:

```python
from critiplot import plot_nos, plot_jbi_case_report, plot_jbi_case_series, plot_grade, plot_robis
```

**Example:**

```python
# NOS
plot_nos("tests/sample_nos.csv", "tests/output_nos.png", theme="blue")

# ROBIS
plot_robis("tests/sample_robis.csv", "tests/output_robis.png", theme="smiley")

# JBI Case Report
plot_jbi_case_report("tests/sample_case_report.csv", "tests/output_case_report.png", theme="gray")

# JBI Case Series
plot_jbi_case_series("tests/sample_case_series.csv", "tests/output_case_series.png", theme="smiley_blue")

# GRADE
plot_grade("tests/sample_grade.csv", "tests/output_grade.png", theme="green")
```

> **Theme options:**
>
> * NOS, JBI Case Report / Case Series, ROBIS: `"default"`, `"blue"`, `"gray"`, `"smiley"`, `"smiley_blue"`
> * GRADE: `"default"`, `"green"`, `"blue"`
> * Default theme is used if omitted.

---

##  Notes

* Generates **traffic-light plots** and **weighted bar charts** using **Matplotlib / Seaborn**.
* Input data must be a CSV or Excel file following each tool’s required columns.
* Critiplot is a **visualization tool only**; it **does not compute risk-of-bias**.

---

## Info

- Web version also exists of this Package.
- Github: https://github.com/aurumz-rgb/Critiplot-main
- Web: https://critiplot.vercel.app

---

## Example / Result
Here’s an example traffic-light plot generated using Critiplot using different themes.

![Example Result](example/result.png)
NOS


![Example Result1](example/grade_result2.png)
GRADE


![Example Result2](example/robis_result5.png)
ROBIS


![Example Result3](example/case_report3.png)
JBI Case Report


![Example Result4](example/series_plot1.png)
JBI Case Series

---

## 📜 License

Apache 2.0 © 2025 Vihaan Sahu

