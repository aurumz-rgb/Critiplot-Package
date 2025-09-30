import streamlit as st
import pandas as pd
import os
import shutil
import tempfile
from io import BytesIO
import base64
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
import seaborn as sns
import sys
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import re


from nos_plot import process_detailed_nos, professional_plot, read_input_file as read_nos_file
from grade_plot import process_grade, grade_plot, read_input_file as read_grade_file
from robis_plot import process_robis, professional_robis_plot, read_input_file as read_robis_file
from jbi_case_report_plot import process_jbi_case_report, professional_jbi_plot, read_input_file as read_jbi_case_file
from jbi_case_series_plot import process_jbi_case_series, professional_jbi_series_plot, read_input_file as read_jbi_series_file

# page configuration
st.set_page_config(
    page_title="Critiplot / Home",
    layout="wide",
    page_icon="./assets/icon.png"  
)

# Hide Streamlit UI elements
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    button[title="Toggle sidebar"] {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


st.markdown("""
<style>
    .stApp { background-color: #111111; }
    h1, h2, h3 { color: #2c3e50; font-weight: 600; }
    .main-content { margin-top: 2vh; }
    .citation-box { border-left: 4px solid #3498db; background-color: #e9ecef; padding: 1rem; margin: 1rem 0; color: #000 !important; }
    .centered-title { 
        text-align: center; 
        font-size: 3.5rem !important;
        font-weight: 800 !important; 
        margin-top: -40px; 
        margin-bottom: 10px; 
        color: #ffffff !important;
    }
    .centered-subtitle { 
        text-align: center; 
        font-size: 1.5rem !important;
        font-weight: 500 !important; 
        margin-bottom: 30px; 
        color: #ffffff !important;
    }
    .quickstart { font-size: 1.4rem; line-height: 1.6; }
    .scrollable-table { overflow-x: auto; }
    .lowered-section { margin-top: 30px; }
    .custom-button {
        background-color: #3498db !important;
        color: white !important;
        text-decoration: none !important;
        padding: 0.5rem 1rem !important;
        font-size: 1rem !important;
        border-radius: 5px !important;
        display: inline-block !important;
        margin: 0 !important;
        transition: background-color 0.3s ease !important;
        border: none !important;
        cursor: pointer !important;
    }
    .custom-button:hover {
        background-color: #2980b9 !important;
    }
    .top-padding-container { margin-top: 100px; }
</style>
""", unsafe_allow_html=True)

# Navigation
active_page = st.session_state.get("active_page", "Home")

st.markdown(f"""
<div style="
    position: absolute;
    top: -1rem;
    left: 0.1rem;
    display: flex;
    gap: 30px;
    padding: 0.1rem 0.1rem;
    background-color: rgba(0,0,0,0);
    z-index: 9999;
    border-radius: 5px;
    font-size: 1.4rem;
    font-weight: 400;
">
    <a href="/" target="_self" style="color: {'#3498db' if active_page=='Home' else '#ffffff'}; text-decoration:none; transition: color 0.3s;" class="nav-link{' active' if active_page=='Home' else ''}">Home</a>
    <a href="/Info" target="_self" style="color: {'#3498db' if active_page=='Info' else '#ffffff'}; text-decoration:none; transition: color 0.3s;" class="nav-link{' active' if active_page=='Info' else ''}">Info</a>
</div>

<style>
div[style*='position: absolute'] a.nav-link {{
    color: #ffffff !important;
}}
div[style*='position: absolute'] a.nav-link:hover:not(.active) {{
    color:#aaaaaa !important;
}}
div[style*='position: absolute'] a.nav-link.active {{
    color: #3498db !important;
}}
</style>
""", unsafe_allow_html=True)

# Background & logo
def add_background_png(png_file):
    if os.path.exists(png_file):
        with open(png_file, "rb") as f:
            b64_img = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{b64_img}");
                background-size: cover;
                background-attachment: fixed;
                padding-top: 0px;
            }}
            </style>
        """, unsafe_allow_html=True)

def display_logo_png_top_touch(png_file, height=180):
    if os.path.exists(png_file):
        with open(png_file, "rb") as f:
            b64_img = base64.b64encode(f.read()).decode()
        st.markdown(f'''
            <div style="text-align:center; margin-top:0px; padding-top:0px;">
                <img src="data:image/png;base64,{b64_img}" height="{height}px" style="display:block; margin:0 auto; padding:0;">
            </div>
        ''', unsafe_allow_html=True)

add_background_png("./assets/background.png")

# Content wrapper
st.markdown('<div class="top-padding-container">', unsafe_allow_html=True)
display_logo_png_top_touch("./assets/logo.png", height=180)
st.markdown('<div class="main-content">', unsafe_allow_html=True)
st.markdown('<h1 class="centered-title">Critiplot.</h1>', unsafe_allow_html=True)
st.markdown('<p class="centered-subtitle">A Critical Appraisal Plot Visualiser for Risk of Bias Assessments</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="lowered-section">', unsafe_allow_html=True)

# Tool selection
tool = st.selectbox(
    "Select Assessment Tool",
    ["NOS (Newcastle-Ottawa Scale)", "GRADE", "ROBIS", "JBI Case Report", "JBI Case Series"],
    key="tool_select"
)

# Quick Start / Data Instructions
st.markdown('<div style="font-size: 1.6rem; font-weight: bold; margin-bottom: 10px;"> Quick Start & Data Instructions</div>', unsafe_allow_html=True)
with st.expander("**Setting Up Your Data**", expanded=True):
    st.markdown('<div class="quickstart" style="margin-top:-1rem;">', unsafe_allow_html=True)
    
    if tool.startswith("NOS"):
        st.write("""
✨  **Critiplot** is a web app for visualizing Newcastle–Ottawa Scale (NOS) risk-of-bias assessments.
It generates:

* **Traffic light plots** showing domain-level judgements for each study.
* **Weighted bar plots** summarizing the distribution of judgements across domains.

All figures are **publication-ready** and formatted to match NOS assessment standards.

---        
             
To work correctly with **Critiplot**, your uploaded table should follow this structure:
    
- **First column:** Study details (Author, Year)
    - **Domain columns:** Each additional column corresponds to a specific NOS domain:
        - Representativeness
        - Non-exposed Selection
        - Exposure Ascertainment
        - Outcome Absent at Start
        - Comparability (Age/Gender)
        - Comparability (Other)
        - Outcome Assessment
        - Follow-up Length
        - Follow-up Adequacy
    - **Total Score:** Sum of the domain scores
    - **Overall RoB:** Overall risk-of-bias judgement for each study (Low, Moderate, High)
    """)
        
        sample_csv_path = "nos_data.csv"
        if os.path.exists(sample_csv_path):
            st.markdown('<div class="scrollable-table">', unsafe_allow_html=True)
            st.dataframe(pd.read_csv(sample_csv_path), width='stretch')
            st.markdown('</div>', unsafe_allow_html=True)

        # Download buttons
        excel_file_path = "nos_data.xlsx"
        csv_file_path = "nos_data.csv"
        def file_to_b64(path):
            if os.path.exists(path):
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            return ""
        st.markdown(f"""
        <div style="display:flex; gap:10px; margin-bottom:10px;">
            <a download="nos_data.xlsx" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{file_to_b64(excel_file_path)}" class="custom-button">
                Excel Template
            </a>
            <a download="nos_data.csv" href="data:text/csv;base64,{file_to_b64(csv_file_path)}" class="custom-button">
                CSV Template
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    elif tool == "GRADE":
        st.write("""
✨  **Critiplot** is a web app for visualizing GRADE assessments.
It generates:

* **Traffic light plots** showing domain-level judgements for each outcome.
* **Weighted bar plots** summarizing the distribution of judgements across domains.

All figures are **publication-ready** and formatted to match GRADE assessment standards.

---        
             
To work correctly with **Critiplot**, your uploaded table should follow this structure:
    
- **Outcome:** Name of the outcome
- **Study:** Study identifier
- **Risk of Bias:** Risk of bias judgement (High, Moderate, Low, Very Low, None)
- **Inconsistency:** Inconsistency judgement (High, Moderate, Low, Very Low, None)
- **Indirectness:** Indirectness judgement (High, Moderate, Low, Very Low, None)
- **Imprecision:** Imprecision judgement (High, Moderate, Low, Very Low, None)
- **Publication Bias:** Publication bias judgement (High, Moderate, Low, Very Low, None)
- **Overall Certainty:** Overall certainty judgement (High, Moderate, Low, Very Low)
    """)
        
        sample_csv_path = "grade_data.csv"
        if os.path.exists(sample_csv_path):
            st.markdown('<div class="scrollable-table">', unsafe_allow_html=True)
            st.dataframe(pd.read_csv(sample_csv_path), width='stretch')
            st.markdown('</div>', unsafe_allow_html=True)

        # Download buttons
        excel_file_path = "grade_data.xlsx"
        csv_file_path = "grade_data.csv"
        def file_to_b64(path):
            if os.path.exists(path):
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            return ""
        st.markdown(f"""
        <div style="display:flex; gap:10px; margin-bottom:10px;">
            <a download="grade_data.xlsx" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{file_to_b64(excel_file_path)}" class="custom-button">
                Excel Template
            </a>
            <a download="grade_data.csv" href="data:text/csv;base64,{file_to_b64(csv_file_path)}" class="custom-button">
                CSV Template
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    elif tool == "ROBIS":
        st.write("""
✨  **Critiplot** is a web app for visualizing ROBIS assessments.
It generates:

* **Traffic light plots** showing domain-level judgements for each review.
* **Weighted bar plots** summarizing the distribution of judgements across domains.

All figures are **publication-ready** and formatted to match ROBIS assessment standards.

---        
             
To work correctly with **Critiplot**, your uploaded table should follow this structure:
    
- **Review:** Review identifier
- **Study Eligibility:** Risk of bias judgement (Low, Unclear, High)
- **Identification & Selection:** Risk of bias judgement (Low, Unclear, High)
- **Data Collection:** Risk of bias judgement (Low, Unclear, High)
- **Synthesis & Findings:** Risk of bias judgement (Low, Unclear, High)
- **Overall Risk:** Overall risk of bias judgement (Low, Unclear, High)
    """)
        
        sample_csv_path = "robis_data.csv"
        if os.path.exists(sample_csv_path):
            st.markdown('<div class="scrollable-table">', unsafe_allow_html=True)
            st.dataframe(pd.read_csv(sample_csv_path), width='stretch')
            st.markdown('</div>', unsafe_allow_html=True)

        # Download buttons
        excel_file_path = "robis_data.xlsx"
        csv_file_path = "robis_data.csv"
        def file_to_b64(path):
            if os.path.exists(path):
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            return ""
        st.markdown(f"""
        <div style="display:flex; gap:10px; margin-bottom:10px;">
            <a download="robis_data.xlsx" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{file_to_b64(excel_file_path)}" class="custom-button">
                Excel Template
            </a>
            <a download="robis_data.csv" href="data:text/csv;base64,{file_to_b64(csv_file_path)}" class="custom-button">
                CSV Template
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    elif tool == "JBI Case Report":
        st.write("""
✨  **Critiplot** is a web app for visualizing JBI Case Report assessments.
It generates:

* **Traffic light plots** showing domain-level judgements for each study.
* **Weighted bar plots** summarizing the distribution of judgements across domains.

All figures are **publication-ready** and formatted to match JBI assessment standards.

---        
             
To work correctly with **Critiplot**, your uploaded table should follow this structure:
    
- **Author,Year:** Study identifier (e.g., "Smith, 2020")
- **Demographics:** Score (0 or 1)
- **History:** Score (0 or 1)
- **ClinicalCondition:** Score (0 or 1)
- **Diagnostics:** Score (0 or 1)
- **Intervention:** Score (0 or 1)
- **PostCondition:** Score (0 or 1)
- **AdverseEvents:** Score (0 or 1)
- **Lessons:** Score (0 or 1)
- **Total:** Sum of the domain scores
- **Overall RoB:** Overall risk of bias judgement (Low, High)
    """)
        
        sample_csv_path = "case_report.csv"
        if os.path.exists(sample_csv_path):
            st.markdown('<div class="scrollable-table">', unsafe_allow_html=True)
            st.dataframe(pd.read_csv(sample_csv_path), width='stretch')
            st.markdown('</div>', unsafe_allow_html=True)

        # Download buttons
        excel_file_path = "case_report.xlsx"
        csv_file_path = "case_report.csv"
        def file_to_b64(path):
            if os.path.exists(path):
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            return ""
        st.markdown(f"""
        <div style="display:flex; gap:10px; margin-bottom:10px;">
            <a download="case_report.xlsx" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{file_to_b64(excel_file_path)}" class="custom-button">
                Excel Template
            </a>
            <a download="case_report.csv" href="data:text/csv;base64,{file_to_b64(csv_file_path)}" class="custom-button">
                CSV Template
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    elif tool == "JBI Case Series":
        st.write("""
✨  **Critiplot** is a web app for visualizing JBI Case Series assessments.
It generates:

* **Traffic light plots** showing domain-level judgements for each study.
* **Weighted bar plots** summarizing the distribution of judgements across domains.

All figures are **publication-ready** and formatted to match JBI assessment standards.

---        
             
To work correctly with **Critiplot**, your uploaded table should follow this structure:
    
- **Author,Year:** Study identifier (e.g., "Smith, 2020")
- **InclusionCriteria:** Score (0 or 1)
- **StandardMeasurement:** Score (0 or 1)
- **ValidIdentification:** Score (0 or 1)
- **ConsecutiveInclusion:** Score (0 or 1)
- **CompleteInclusion:** Score (0 or 1)
- **Demographics:** Score (0 or 1)
- **ClinicalInfo:** Score (0 or 1)
- **Outcomes:** Score (0 or 1)
- **SiteDescription:** Score (0 or 1)
- **Statistics:** Score (0 or 1)
- **Total:** Sum of the domain scores
- **Overall RoB:** Overall risk of bias judgement (Low, High)
    """)
        
        sample_csv_path = "case_series.csv"
        if os.path.exists(sample_csv_path):
            st.markdown('<div class="scrollable-table">', unsafe_allow_html=True)
            st.dataframe(pd.read_csv(sample_csv_path), width='stretch')
            st.markdown('</div>', unsafe_allow_html=True)

        # Download buttons
        excel_file_path = "case_series.xlsx"
        csv_file_path = "case_series.csv"
        def file_to_b64(path):
            if os.path.exists(path):
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            return ""
        st.markdown(f"""
        <div style="display:flex; gap:10px; margin-bottom:10px;">
            <a download="case_series.xlsx" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{file_to_b64(excel_file_path)}" class="custom-button">
                Excel Template
            </a>
            <a download="case_series.csv" href="data:text/csv;base64,{file_to_b64(csv_file_path)}" class="custom-button">
                CSV Template
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Upload & process
st.markdown("### Upload Your Data")
st.markdown('<p style="color: #ffff; font-size: 1.1rem;">Please upload your file in <b>CSV</b> or <b>Excel (.xlsx)</b> format. <b>Maximum file size: 20MB per file.</b></p>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv","xls","xlsx"], key=f"file_uploader_{tool}")

# Theme selection per tool
if tool.startswith("NOS"):
    theme_options = ["default", "blue", "gray", "smiley", "smiley_blue"]
elif tool == "GRADE":
    theme_options = ["default", "green", "blue"]
elif tool == "ROBIS":
    theme_options = ["default", "blue", "gray", "smiley", "smiley_blue"]
elif tool == "JBI Case Report":
    theme_options = ["default", "blue", "gray", "smiley", "smiley_blue"]
elif tool == "JBI Case Series":
    theme_options = ["default", "blue", "gray", "smiley", "smiley_blue"]

theme = st.selectbox(
    "Select Plot Theme",
    theme_options,
    key=f"theme_{tool}"
)

# Initialize variables
df = None
tmp_file_path = None
temp_dir = None

if uploaded_file is not None:
    try:
        # Validate file size (20MB limit)
        if uploaded_file.size > 20 * 1024 * 1024:  
            st.error("❌ File size exceeds the 20MB limit per file. Please upload a smaller file.")
            st.stop()
            
        # Validate file format
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        if file_ext not in ['.csv', '.xlsx', '.xls']:
            st.error(f"❌ Invalid file format: '{file_ext}'. Please upload a CSV or Excel file.")
            st.stop()
            
        # Create a temporary file to pass to the imported functions
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        # Process data based on selected tool
        if tool.startswith("NOS"):
            df = read_nos_file(tmp_file_path)
            df = process_detailed_nos(df)
            st.success(" Data validated successfully!")
            plot_function = professional_plot
            plot_name = "NOS"
        elif tool == "GRADE":
            df = read_grade_file(tmp_file_path)
            df = process_grade(df)
            st.success(" Data validated successfully!")
            plot_function = grade_plot
            plot_name = "GRADE"
        elif tool == "ROBIS":
            df = read_robis_file(tmp_file_path)
            df = process_robis(df)
            st.success(" Data validated successfully!")
            plot_function = professional_robis_plot
            plot_name = "ROBIS"
        elif tool == "JBI Case Report":
            df = read_jbi_case_file(tmp_file_path)
            df = process_jbi_case_report(df)
            st.success(" Data validated successfully!")
            plot_function = professional_jbi_plot
            plot_name = "JBI_Case_Report"
        elif tool == "JBI Case Series":
            df = read_jbi_series_file(tmp_file_path)
            df = process_jbi_case_series(df)
            st.success(" Data validated successfully!")
            plot_function = professional_jbi_series_plot
            plot_name = "JBI_Case_Series"

        # Create temporary directory for output files
        temp_dir = tempfile.mkdtemp()
        output_files = {ext: os.path.join(temp_dir, f"{plot_name}_TrafficLight{ext}") for ext in [".png",".pdf",".svg",".eps"]}
        
        # Generate plots
        for out_ext, path in output_files.items():
            plot_function(df, path, theme=theme)
            plt.close('all')  # Close all figures to free memory

        st.markdown("### Visualization Preview")
        st.image(output_files[".png"], width='stretch')

        # Download buttons
        st.markdown("###  Download Visualization")
        st.markdown('<p style="color: #ffff; font-size: 1.1rem;">Download your Critiplot visualisation in formats like:</p>', unsafe_allow_html=True)

        download_html = '<div style="display:flex; gap:10px; margin-bottom:10px;">'
        for out_ext, path in output_files.items():
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            mime = {".png":"image/png",".pdf":"application/pdf",".svg":"image/svg+xml",".eps":"application/postscript"}[out_ext]
            download_html += f'<a download="{plot_name}_TrafficLight{out_ext}" href="data:{mime};base64,{b64}" class="custom-button">{out_ext[1:].upper()}</a>'
        download_html += "</div>"
        st.markdown(download_html, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.markdown("Please ensure your file follows the template structure shown above.")
    finally:
        # Clean up temporary files
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        # Clear dataframe from memory
        df = None
        # Force garbage collection
        import gc
        gc.collect()

# Citation Section
st.markdown("---")
st.markdown("## Citation")


apa_citation = (
    "Sahu, V. (2025). Critiplot: A Critical Appraisal Plot Visualiser for Risk of Bias in Systematic Reviews and Meta-Analyses (v1.0.1). "
    "Zenodo. https://doi.org/10.5281/zenodo.17236600"
)

harvard_citation = (
    "Sahu, V., 2025. Critiplot: A Critical Appraisal Plot Visualiser for Risk of Bias in Systematic Reviews and Meta-Analyses (v1.0.1). "
    "Zenodo. Available at: https://doi.org/10.5281/zenodo.17236600"
)

mla_citation = (
    "Sahu, Vihaan. \"Critiplot: A Critical Appraisal Plot Visualiser for Risk of Bias in Systematic Reviews and Meta-Analyses (v1.0.1).\" "
    "2025, Zenodo, https://doi.org/10.5281/zenodo.17236600."
)

chicago_citation = (
    "Sahu, Vihaan. 2025. \"Critiplot: A Critical Appraisal Plot Visualiser for Risk of Bias in Systematic Reviews and Meta-Analyses (v1.0.1).\" "
    "Zenodo. https://doi.org/10.5281/zenodo.17236600."
)

ieee_citation = (
    "V. Sahu, \"Critiplot: A Critical Appraisal Plot Visualiser for Risk of Bias in Systematic Reviews and Meta-Analyses (v1.0.1),\" "
    "Zenodo, 2025. doi: 10.5281/zenodo.17236600."
)

vancouver_citation = (
    "Sahu V. Critiplot: A Critical Appraisal Plot Visualiser for Risk of Bias in Systematic Reviews and Meta-Analyses (v1.0.1). "
    "Zenodo. 2025. doi:10.5281/zenodo.17236600"
)

ris_data = """TY  - JOUR
AU  - Sahu, V
TI  - Critiplot: A Critical Appraisal Plot Visualiser for Risk of Bias in Systematic Reviews and Meta-Analyses (v1.0.1)
PY  - 2025
DO  - 10.5281/zenodo.17236600
ER  -"""

bib_data = """@misc{Sahu2025,
  author={Sahu, V.},
  title={Critiplot: A Critical Appraisal Plot Visualiser for Risk of Bias in Systematic Reviews and Meta-Analyses (v1.0.1)},
  year={2025},
  doi={10.5281/zenodo.17236600}
}"""


citation_style = st.selectbox(
    "Select citation style",
    ["APA", "Harvard", "MLA", "Chicago", "IEEE", "Vancouver"]
)


if citation_style == "APA":
    citation_text = apa_citation
elif citation_style == "Harvard":
    citation_text = harvard_citation
elif citation_style == "MLA":
    citation_text = mla_citation
elif citation_style == "Chicago":
    citation_text = chicago_citation
elif citation_style == "IEEE":
    citation_text = ieee_citation
elif citation_style == "Vancouver":
    citation_text = vancouver_citation

st.markdown(f'<p style="margin:0; color:#ffff; font-size:1.1rem;"><i>If you use Critiplot to create risk-of-bias plots for your study, please remember to cite the tool.</i></p>', unsafe_allow_html=True)
st.markdown(f'<div class="citation-box"><p style="margin:0; color: #000;">{citation_text}</p></div>', unsafe_allow_html=True)

copy_button_html = f"""
<style>
.custom-button {{
    background-color: #3498db !important;
    color: white !important;
    text-decoration: none !important;
    padding: 0.5rem 1rem !important;
    font-size: 1rem !important;
    border-radius: 5px !important;
    display: inline-block !important;
    margin: 0 !important;
    transition: background-color 0.3s ease !important;
    border: none !important;
    cursor: pointer !important;
}}
.custom-button:hover {{
    background-color: #2980b9 !important;
}}
</style>

<div style="display:flex; gap:10px; margin-top:10px; margin-bottom:10px; position:relative;" id="button-container">
    <a id="copy-btn" class="custom-button">Copy Citation</a>
    <a download="Critiplot_citation.ris" href="data:application/x-research-info-systems;base64,{base64.b64encode(ris_data.encode()).decode()}" class="custom-button">RIS Format</a>
    <a download="Critiplot_citation.bib" href="data:application/x-bibtex;base64,{base64.b64encode(bib_data.encode()).decode()}" class="custom-button">BibTeX Format</a>
</div>

<script>
document.getElementById("copy-btn").onclick = function() {{
    const text = `{citation_text}`;
    const btn = document.getElementById("copy-btn");
    navigator.clipboard.writeText(text).then(() => {{
        const originalText = btn.innerText;
        btn.innerText = "Copied!";
        setTimeout(() => {{ btn.innerText = originalText; }}, 2000);
    }});
}};
</script>
"""
components.html(copy_button_html, height=100)

# Footer
st.markdown("---")
st.markdown("""
<style>
.footer-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #fff;
    padding: 1rem;
    font-size: 1.05rem;
}
.footer-left { text-align:left; }
.footer-center { display:flex; gap:40px; justify-content:center; align-items:center; }
.footer-link { color:#3498db; text-decoration:none; transition:color 0.3s ease; }
.footer-link:hover { color:#5682B1; }
</style>

<div class="footer-container">
    <div class="footer-left">
        <div>© 2025 Vihaan Sahu</div>
        <div>Licensed under the Apache License, Version 2.0</div>
    </div>
    <div class="footer-center">
        <span>Critiplot</span>
        <span>Professional Risk of Bias Visualization Tool</span>
        <a href='https://github.com/aurumz-rgb/Critiplot-main' target='_blank' class='footer-link'>GitHub Repository</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Close wrappers
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)