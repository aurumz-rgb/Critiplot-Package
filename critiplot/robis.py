import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os
from matplotlib.lines import Line2D
from collections import defaultdict

def process_robis(df: pd.DataFrame) -> pd.DataFrame:
    """Process ROBIS data with memory optimizations"""
    column_map = {
        "Study Eligibility Criteria": "Study Eligibility",
        "Identification & Selection of Studies": "Identification & Selection",
        "Data Collection & Study Appraisal": "Data Collection",
        "Overall RoB": "Overall Risk"
    }
    df = df.rename(columns=column_map)

    required_columns = [
        "Review",
        "Study Eligibility",
        "Identification & Selection",
        "Data Collection",
        "Synthesis & Findings",
        "Overall Risk"
    ]
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df

def risk_to_symbol(risk: str) -> str:
    """Convert risk level to symbol"""
    if risk == "Low":
        return "☺"
    elif risk == "Unclear":
        return "😐"
    elif risk == "High":
        return "☹"
    return "?"

def standardize_risk(risk):
    """Standardize risk level input"""
    risk = str(risk).strip().lower()
    if risk in ['high', 'h']:
        return 'High'
    elif risk in ['unclear', 'uncertain', 'u']:
        return 'Unclear'
    elif risk in ['low', 'l']:
        return 'Low'
    else:
        return 'Unclear'

def professional_robis_plot(df: pd.DataFrame, output_file: str, theme: str = "default"):
    """Create professional ROBIS plot with balanced font sizes"""
    theme_options = {
        "default": {"Low":"#06923E","Unclear":"#FFD93D","High":"#DC2525"},
        "blue": {"Low":"#3a83b7","Unclear":"#7fb2e6","High":"#084582"},
        "gray": {"Low":"#63BF93FF","Unclear":"#5B6D80","High":"#FF884DFF"},
        "smiley": {"Low":"#06923E","Unclear":"#FFD93D","High":"#DC2525"},
        "smiley_blue": {"Low":"#3a83b7","Unclear":"#7fb2e6","High":"#084582"}
    }

    if theme not in theme_options:
        raise ValueError(f"Theme {theme} not available. Choose from {list(theme_options.keys())}")
    colors = theme_options[theme]

    domains = ["Study Eligibility","Identification & Selection","Data Collection","Synthesis & Findings","Overall Risk"]
    

    n_studies = len(df)
    per_study_height = 0.65      
    min_first_plot_height = 3.0  
    second_plot_height = 3.5  
    gap_between_plots = 1.7    
    top_margin = 1.0           
    bottom_margin = 0.5        
    
    first_plot_height = max(min_first_plot_height, n_studies * per_study_height)
    total_height = first_plot_height + gap_between_plots + second_plot_height + top_margin + bottom_margin
    
    fig = plt.figure(figsize=(24, total_height))
    

    ax0_bottom = (bottom_margin + second_plot_height + gap_between_plots) / total_height
    ax0_height = first_plot_height / total_height
    ax1_bottom = bottom_margin / total_height
    ax1_height = second_plot_height / total_height
    
    ax0 = fig.add_axes([0.12, ax0_bottom, 0.75, ax0_height])
    ax1 = fig.add_axes([0.12, ax1_bottom, 0.75, ax1_height])
    
  
    domain_pos = {d: i for i, d in enumerate(domains)}
    review_pos = {a: i for i, a in enumerate(df["Review"].tolist())}
    
    
    for y in range(len(review_pos)):
        ax0.axhline(y, color='lightgray', linewidth=0.8, zorder=0)
    ax0.axhline(-0.5, color='lightgray', linewidth=0.8, zorder=0)
    ax0.axhline(len(review_pos)-0.5, color='lightgray', linewidth=0.8, zorder=0)
    
    if theme.startswith("smiley"):
    
        for _, row in df.iterrows():
            y_pos = review_pos[row["Review"]]
            
            for domain in domains:
                risk = standardize_risk(row[domain])
                symbol = risk_to_symbol(risk)
                x_pos = domain_pos[domain]
                ax0.text(x_pos, y_pos, symbol, fontsize=32, ha='center', va='center',
                        color=colors.get(risk, "#BBBBBB"), fontweight="bold", zorder=1)
    else:

        x_coords = []
        y_coords = []
        point_colors = []
        
        for _, row in df.iterrows():
            y_pos = review_pos[row["Review"]]
            
            for domain in domains:
                risk = standardize_risk(row[domain])
                x_coords.append(domain_pos[domain])
                y_coords.append(y_pos)
                point_colors.append(colors.get(risk, "#BBBBBB"))
        
        ax0.scatter(x_coords, y_coords, c=point_colors, s=1300, marker="s", 
                   edgecolor='white', linewidth=1, zorder=1)
    

    ax0.set_xticks(range(len(domains)))
    ax0.set_xticklabels(domains, fontsize=20, fontweight="bold")
    ax0.set_yticks(list(review_pos.values()))
    ax0.set_yticklabels(list(review_pos.keys()), fontsize=20, fontweight="bold")
    ax0.set_ylim(-0.5, len(review_pos)-0.5)
    ax0.set_xlim(-0.5, len(domains)-0.5)
    ax0.set_facecolor('white')
    ax0.set_title("ROBIS Traffic-Light Plot", fontsize=28, fontweight="bold", pad=12)
    ax0.set_xlabel("")
    ax0.set_ylabel("")
    ax0.grid(axis='x', linestyle='--', alpha=0.25)
    
  
    bar_data = defaultdict(lambda: defaultdict(int))
    
    for _, row in df.iterrows():
        for domain in domains:
            risk = standardize_risk(row[domain])
            bar_data[domain][risk] += 1
    
    
    total_reviews = len(df)
    for domain in bar_data:
        for risk in bar_data[domain]:
            bar_data[domain][risk] = (bar_data[domain][risk] / total_reviews) * 100
    
    inverted_domains = domains[::-1]
    bar_height = 0.90
    
    
    bottom = None
    for risk in ["High", "Unclear", "Low"]:
        values = [bar_data[domain].get(risk, 0) for domain in inverted_domains]
        ax1.barh(
            inverted_domains, 
            values, 
            left=bottom, 
            color=colors.get(risk, "#BBBBBB"), 
            edgecolor='black', 
            label=risk, 
            height=bar_height
        )
        if bottom is None:
            bottom = values
        else:
            bottom = [b + v for b, v in zip(bottom, values)]
    
   
    for i, domain in enumerate(inverted_domains):
        left = 0
        for risk in ["High", "Unclear", "Low"]:
            width = bar_data[domain].get(risk, 0)
            if width > 0:
                ax1.text(left + width/2, i, f"{width:.0f}%", 
                        ha='center', va='center', color='black', 
                        fontsize=18, fontweight="bold")
                left += width
    

    ax1.set_xlim(0, 100)
    ax1.set_xlabel("Percentage of Reviews (%)", fontsize=24, fontweight="bold")
    ax1.tick_params(axis='x', labelsize=20)
    ax1.set_ylabel("")
    ax1.set_title("Distribution of Risk-of-Bias Judgments by Domain", fontsize=28, fontweight="bold")
    ax1.grid(axis='x', linestyle='--', alpha=0.25)
    ax1.set_yticks(range(len(inverted_domains)))
    ax1.set_yticklabels(inverted_domains, fontsize=20, fontweight="bold")
    
    for label in ax1.get_yticklabels():
        label.set_fontweight("bold")
    for label in ax1.get_xticklabels():
        label.set_fontweight("bold")
    
    for y in range(len(inverted_domains)):
        ax1.axhline(y-0.5, color='lightgray', linewidth=0.8, zorder=0)
    
 
    legend_elements = [
        Line2D([0], [0], marker='s', color='w', label='Low Risk', 
              markerfacecolor=colors.get("Low", "#BBBBBB"), markersize=18),
        Line2D([0], [0], marker='s', color='w', label='Unclear Risk', 
              markerfacecolor=colors.get("Unclear", "#BBBBBB"), markersize=18),
        Line2D([0], [0], marker='s', color='w', label='High Risk', 
              markerfacecolor=colors.get("High", "#BBBBBB"), markersize=18)
    ]
    legend = ax0.legend(
        handles=legend_elements, 
        title="Domain Risk",
        bbox_to_anchor=(1.02, 1), 
        loc='upper left',
        fontsize=20, 
        title_fontsize=22
    )
    legend.get_frame().set_edgecolor('black')
    plt.setp(legend.get_texts(), fontweight="normal")
    plt.setp(legend.get_title(), fontweight="bold")


    valid_ext = [".png", ".pdf", ".svg", ".eps"]
    ext = os.path.splitext(output_file)[1].lower()
    if ext not in valid_ext:
        raise ValueError(f"Unsupported file format: {ext}. Use one of {valid_ext}")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ ROBIS professional plot saved to {output_file}")
    

    del bar_data

def read_input_file(file_path: str) -> pd.DataFrame:
    """Read input file with memory optimizations"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(file_path, engine='c')
    elif ext in [".xls", ".xlsx"]:
        return pd.read_excel(file_path, engine='openpyxl')
    else:
        raise ValueError(f"Unsupported file format: {ext}. Provide a CSV or Excel file.")

def plot_robis(input_file: str, output_file: str, theme: str = "default"):
    """
    Generate a ROBIS (Risk Of Bias In Systematic reviews) plot from input data.
    
    Parameters:
    -----------
    input_file : str
        Path to the input CSV or Excel file containing ROBIS data
    output_file : str
        Path where the output plot will be saved (supports .png, .pdf, .svg, .eps)
    theme : str, optional
        Color theme for the plot. Options: "default", "blue", "gray", "smiley", "smiley_blue"
        Default is "default"
    
    Returns:
    --------
    None
        The plot is saved to the specified output file path
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    df = read_input_file(input_file)
    df = process_robis(df)
    professional_robis_plot(df, output_file, theme)

if __name__ == "__main__":
    if len(sys.argv) not in [3,4]:
        print("Usage: python3 robis_plot.py input_file output_file.(png|pdf|svg|eps) [theme]")
        sys.exit(1)

    input_file, output_file = sys.argv[1], sys.argv[2]
    theme = sys.argv[3] if len(sys.argv) == 4 else "default"

    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)

    df = read_input_file(input_file)
    df = process_robis(df)
    professional_robis_plot(df, output_file, theme)
    
    del df