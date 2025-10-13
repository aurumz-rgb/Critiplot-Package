
###  `INSTRUCTIONS.md`

````markdown
# Critiplot – Instructions

**Critiplot** is an open-source Python package for **visualizing risk-of-bias (RoB) assessments** across multiple evidence-synthesis tools:

- **Newcastle–Ottawa Scale (NOS)**
- **JBI Critical Appraisal Checklists** (Case Report / Case Series)
- **GRADE** (Certainty of Evidence)
- **ROBIS** (Risk of Bias in Systematic Reviews)

It produces **publication-ready traffic-light plots** and **stacked bar charts** for summarizing study quality in systematic reviews and meta-analyses.

📦 **Python Package:** [https://pypi.org/project/critiplot/1.0.1/](https://pypi.org/project/critiplot/1.0.1/)

---

## 🧩 Installation

### Install from PyPI
```bash
pip install critiplot
````

### Or install locally from source

```bash
# Clone repository
git clone https://github.com/aurumz-rgb/Critiplot-Package.git
cd Critiplot-Package

# Install requirements
pip install -r requirements.txt

# Install package locally
pip install .
```

**Requirements:**
Python 3.11, Matplotlib, Seaborn, and Pandas.

---

## ⚡ Usage

Import plotting functions from the package:

```python
from critiplot import plot_nos, plot_jbi_case_report, plot_jbi_case_series, plot_grade, plot_robis
```

### Example Usage

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

---

## 🎨 Themes

Critiplot supports a variety of **themes** that modify the color palette and style of plots.
Each theme automatically adjusts traffic-light colors and figure aesthetics for better publication compatibility.

| Tool / Assessment   | Available Themes                                             | Description                                                       |
| ------------------- | ------------------------------------------------------------ | ----------------------------------------------------------------- |
| **NOS, JBI, ROBIS** | `"default"`, `"blue"`, `"gray"`, `"smiley"`, `"smiley_blue"` | Traffic-light palettes and neutral tints for medical publications |
| **GRADE**           | `"default"`, `"green"`, `"blue"`                             | Confidence or certainty scales (green preferred)                  |

### Applying a Theme

Each plotting function accepts a `theme` argument:

```python
plot_nos("tests/sample_nos.csv", theme="smiley")
```

If no theme is specified, the **default theme** is applied automatically.

---

##  Input Data Format

Critiplot accepts **CSV** or **Excel (`.xlsx`)** input files containing structured risk-of-bias data.
Each file should include the relevant **domains** required by the selected assessment tool.

### Example Format (for Newcastle–Ottawa Scale)

| Study   | Domain 1 | Domain 2 | Domain 3 | Overall  |
| ------- | -------- | -------- | -------- | -------- |
| Study A | Low      | Unclear  | High     | Moderate |
| Study B | Low      | Low      | Low      | Low      |

 **Values** such as `Low`, `High`, `Unclear`, or `Moderate` are automatically **color-coded** according to the selected theme.
Each domain column represents a domain of bias or quality, and Critiplot uses these to generate **traffic-light plots** and **weighted summary charts**.

---

### 📂 Example Datasets

For reproducibility and reference, example `.csv` and `.xlsx` files are included in the repository:

| Tool / Assessment Type           | Example Files                                                   |
| -------------------------------- | --------------------------------------------------------------- |
| **Newcastle–Ottawa Scale (NOS)** | `tests/sample_nos.csv`, `tests/sample_nos.xlsx`                 |
| **ROBIS**                        | `tests/sample_robis.csv`, `tests/sample_robis.xlsx`             |
| **GRADE**                        | `tests/sample_grade.csv`, `tests/sample_grade.xlsx`             |
| **JBI Case Report**              | `tests/sample_case_report.csv`, `tests/sample_case_report.xlsx` |
| **JBI Case Series**              | `tests/sample_case_series.csv`, `tests/sample_case_series.xlsx` |

You can **open these files directly** to view the expected column format and data layout for each plotting function.

---

##  Output

Each plotting function generates:

* A **Matplotlib figure**
* Optional image output (`.png`, `.svg`)
* Customizable colors, titles, and legends

Example:

```python
plot_nos("tests/sample_nos.csv", save_as="my_plot.svg", show=True)
```

---

## ⚙️ Notes

* Critiplot **only visualizes** risk-of-bias; it does **not calculate** RoB scores.
* Input files must be structured correctly according to the selected tool.
* Ideal for inclusion in **systematic reviews**, **evidence synthesis**, and **meta-analysis** publications.

---

## 🧪 Reproducibility (for JOSS Reviewers)

All results in the paper can be reproduced by:

1. Installing dependencies:

   ```bash
   pip install -r requirements.txt
   ```
2. Running any example commands from this document.
3. Using the sample input files under the `tests/` directory.

---

## 🌐 Additional Information

* **GitHub:** [https://github.com/aurumz-rgb/Critiplot-Package](https://github.com/aurumz-rgb/Critiplot-Package)
* **Web Demo:** [https://critiplot.vercel.app](https://critiplot.vercel.app)

