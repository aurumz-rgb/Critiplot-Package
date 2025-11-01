
![Preview](assets/preview1.png)

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17338087.svg)](https://doi.org/10.5281/zenodo.17338087)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/critiplot?period=total&units=INTERNATIONAL_SYSTEM&left_color=GREY&right_color=BLUE&left_text=downloads)](https://pepy.tech/projects/critiplot)

**Critiplot** is an open-source Python package for **visualizing risk-of-bias (RoB) assessments** across multiple evidence synthesis tools:

* **Newcastle-Ottawa Scale (NOS)**

* **JBI Critical Appraisal Checklists** (Case Report / Case Series)

* **GRADE certainty of evidence**

* **ROBIS for systematic reviews**

* It produces **publication-ready traffic-light plots** and **stacked bar charts** for summarizing study quality.

* **Python Package**: [https://pypi.org/project/critiplot/1.0.2/](https://pypi.org/project/critiplot/1.0.2/)

---

## 📥 Installation

You can install **Critiplot** directly from PyPI:

```bash
pip install critiplot
```

Or install locally from source:

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
import critiplot

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
## Sample

![Python Result](example/python.png)

---

## Notes

* Generates **traffic-light plots** and **weighted bar charts** using **Matplotlib / Seaborn**.
* Input data must be a CSV or Excel file following each tool’s required columns.
* Critiplot is a **visualization tool only**; it **does not compute risk-of-bias**.

---

## Info

* Web version also exists for this package.
* GitHub: [https://github.com/aurumz-rgb/Critiplot-main](https://github.com/aurumz-rgb/Critiplot-main)
* Web: [https://critiplot.vercel.app](https://critiplot.vercel.app)

---

## Citation

If you use this software, please cite it using the following metadata:

```yaml
cff-version: 1.2.0
message: "If you use this software, please cite it using the following metadata."
title: "Critiplot: A Python based Package for risk-of-bias data visualization in Systematic Reviews & Meta-Analysis"
version: "v1.0.2"
doi: "10.5281/zenodo.17338087"
date-released: 2025-09-06
authors:
  - family-names: "Sahu"
    given-names: "Vihaan"
preferred-citation:
  type: software
  authors:
    - family-names: "Sahu"
      given-names: "Vihaan"
  title: "Critiplot: A Python based Package for risk-of-bias data visualization in Systematic Reviews & Meta-Analysis"
  version: "v1.0.2"
  doi: "10.5281/zenodo.17338087"
  year: 2025
  url: "https://doi.org/10.5281/zenodo.17338087"
```

Or cite as:

> **Sahu, V. (2025). *Critiplot: A Python based Package for risk-of-bias data visualization in Systematic Reviews & Meta-Analysis* (v1.0.2). Zenodo. [https://doi.org/10.5281/zenodo.17338087](https://doi.org/10.5281/zenodo.17338087)**


---

## 📜 License

Apache 2.0 © 2025 Vihaan Sahu

---


## Example / Result

Here’s an example traffic-light plot generated using Critiplot with different themes:

![Example Result](example/result.png)
![Example Result11](example/result1.png)
![Example Result22](example/result2.png)
![Example Result33](example/nos_result.png)
![Example Result44](example/nos_result2.png)
**NOS**


![Example Result1](example/grade_result2.png)
![Example Result12](example/grade_result1.png)
![Example Result13](example/grade_result3.png)
**GRADE**


![Example Result2](example/robis_result5.png)
![Example Result21](example/robis_result4.png)
![Example Result23](example/robis_result3.png)
![Example Result29](example/robis_result2.png)
![Example Result26](example/robis_result1.png)
**ROBIS**


![Example Result3](example/case_report3.png)
![Example Result34](example/case_report.png)
![Example Result36](example/case_report1.png)
![Example Result37](example/case_report2.png)
![Example Result38](example/case_report4.png)
**JBI Case Report**


![Example Result4](example/series_plot1.png)
![Example Result41](example/series_plot.png)
![Example Result42](example/series_plot2.png)
![Example Result43](example/series_plot4.png)
![Example Result46](example/series_plot5.png)
**JBI Case Series**
