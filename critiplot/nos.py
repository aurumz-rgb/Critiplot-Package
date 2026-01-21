import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
from collections import defaultdict
from matplotlib.lines import Line2D


def process_detailed_nos(df: pd.DataFrame) -> pd.DataFrame:
    """Process NOS data with validation and memory optimizations"""
    required_columns = [
        "Author, Year",
        "Representativeness", "Non-exposed Selection", "Exposure Ascertainment", "Outcome Absent at Start",
        "Comparability (Age/Gender)", "Comparability (Other)",
        "Outcome Assessment", "Follow-up Length", "Follow-up Adequacy",
        "Total Score", "Overall RoB"
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    numeric_cols = required_columns[1:-2]
    for col in numeric_cols:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise ValueError(f"Column {col} must be numeric.")
        if df[col].min() < 0 or df[col].max() > 5:
            raise ValueError(f"Column {col} contains invalid star values (0-5 allowed).")

    df["Selection"] = df["Representativeness"] + df["Non-exposed Selection"] + df["Exposure Ascertainment"] + df["Outcome Absent at Start"]
    df["Comparability"] = df["Comparability (Age/Gender)"] + df["Comparability (Other)"]
    df["Outcome/Exposure"] = df["Outcome Assessment"] + df["Follow-up Length"] + df["Follow-up Adequacy"]

    df["ComputedTotal"] = df["Selection"] + df["Comparability"] + df["Outcome/Exposure"]
    mismatches = df[df["ComputedTotal"] != df["Total Score"]]
    if not mismatches.empty:
        print("⚠️ Warning: Total Score mismatches detected:")
        print(mismatches[["Author, Year", "Total Score", "ComputedTotal"]])

    return df

def stars_to_rob(stars, domain):
    """Convert stars to risk of bias"""
    if domain == "Selection":
        return "Low" if stars >= 3 else "Moderate" if stars == 2 else "High"
    elif domain == "Comparability":
        return "Low" if stars == 2 else "Moderate" if stars == 1 else "High"
    elif domain == "Outcome/Exposure":
        return "Low" if stars == 3 else "Moderate" if stars == 2 else "High"
    return "High"

def map_color(stars, domain, colors):
    """Map stars to color based on domain"""
    risk = stars_to_rob(stars, domain)
    return colors.get(risk, "#BBBBBB")

def professional_plot(df: pd.DataFrame, output_file: str, theme: str = "default"):
    """Create professional NOS plot with optimized layout and rendering"""
    theme_options = {
        "default": {"Low":"#2E7D32", "Moderate":"#F9A825", "High":"#C62828"},
        "blue": {"Low":"#3a83b7","Moderate":"#bdcfe7","High":"#084582"},
        "gray": {"Low":"#63BF93FF","Moderate":"#5B6D80","High":"#FF884DFF"},
        "smiley": {"Low":"#2E7D32", "Moderate":"#F9A825", "High":"#C62828"},
        "smiley_blue": {"Low":"#3a83b7","Moderate":"#7fb2e6","High":"#084582"}
    }

    if theme not in theme_options:
        raise ValueError(f"Theme {theme} not available. Choose from {list(theme_options.keys())}")
    colors = theme_options[theme]

    domains = ["Selection", "Comparability", "Outcome/Exposure", "Overall RoB"]
    

    n_studies = len(df)
    per_study_height = 0.65
    min_first_plot_height = 4.0
    second_plot_height = 2.4
    gap_between_plots = 1.7
    top_margin = 1.0
    bottom_margin = 0.5
    
    first_plot_height = max(min_first_plot_height, n_studies * per_study_height)
    total_height = first_plot_height + gap_between_plots + second_plot_height + top_margin + bottom_margin
    
    fig = plt.figure(figsize=(18, total_height))
    

    ax0_bottom = (bottom_margin + second_plot_height + gap_between_plots) / total_height
    ax0_height = first_plot_height / total_height
    ax1_bottom = bottom_margin / total_height
    ax1_height = second_plot_height / total_height
    
    ax0 = fig.add_axes([0.12, ax0_bottom, 0.75, ax0_height])
    ax1 = fig.add_axes([0.12, ax1_bottom, 0.75, ax1_height])
    
    domain_pos = {d: i for i, d in enumerate(domains)}
    author_pos = {a: i for i, a in enumerate(df["Author, Year"].tolist())}
    

    for y in range(len(author_pos)):
        ax0.axhline(y, color='lightgray', linewidth=0.8, zorder=0)
    ax0.axhline(-0.5, color='lightgray', linewidth=0.8, zorder=0)
    ax0.axhline(len(author_pos)-0.5, color='lightgray', linewidth=0.8, zorder=0)
    
    if theme.startswith("smiley"):

        symbol_map = {"Low": "☺", "Moderate": "😐", "High": "☹"}
        
        for _, row in df.iterrows():
            y_pos = author_pos[row["Author, Year"]]
            

            for domain in domains[:-1]:
                stars = row[domain]
                risk = stars_to_rob(stars, domain)
                symbol = symbol_map.get(risk, "?")
                x_pos = domain_pos[domain]
                ax0.text(x_pos, y_pos, symbol, fontsize=35, ha='center', va='center', 
                        color=colors[risk], fontweight='bold', zorder=1)
            

            overall_rob = row["Overall RoB"]
            symbol = symbol_map.get(overall_rob, "?")
            x_pos = domain_pos["Overall RoB"]
            ax0.text(x_pos, y_pos, symbol, fontsize=35, ha='center', va='center', 
                    color=colors.get(overall_rob, "#BBBBBB"), fontweight='bold', zorder=1)
    else:

        x_coords = []
        y_coords = []
        point_colors = []
        
        for _, row in df.iterrows():
            y_pos = author_pos[row["Author, Year"]]
            
            for domain in domains[:-1]:
                stars = row[domain]
                risk = stars_to_rob(stars, domain)
                x_coords.append(domain_pos[domain])
                y_coords.append(y_pos)
                point_colors.append(colors[risk])
            
            overall_rob = row["Overall RoB"]
            x_coords.append(domain_pos["Overall RoB"])
            y_coords.append(y_pos)
            point_colors.append(colors.get(overall_rob, "#BBBBBB"))
        
        ax0.scatter(x_coords, y_coords, c=point_colors, s=1200, marker="s", 
                   edgecolor='white', linewidth=1, zorder=1)
    

    ax0.set_xticks(range(len(domains)))
    ax0.set_xticklabels(domains, fontsize=21, fontweight="bold")
    ax0.set_yticks(list(author_pos.values()))
    ax0.set_yticklabels(list(author_pos.keys()), fontsize=19, fontweight="bold", rotation=0)
    ax0.set_ylim(-0.5, len(author_pos)-0.5)
    ax0.set_xlim(-0.5, len(domains)-0.5)
    ax0.set_facecolor('white')
    ax0.set_title("NOS Traffic-Light Plot", fontsize=27, fontweight="bold", pad=12)
    ax0.set_xlabel("")
    ax0.set_ylabel("")
    ax0.grid(axis='x', linestyle='--', alpha=0.25)
    

    bar_data = defaultdict(lambda: defaultdict(int))
    
    for _, row in df.iterrows():
        for domain in domains[:-1]:
            risk = stars_to_rob(row[domain], domain)
            bar_data[domain][risk] += 1
        bar_data["Overall RoB"][row["Overall RoB"]] += 1
    

    total_studies = len(df)
    for domain in bar_data:
        for risk in bar_data[domain]:
            bar_data[domain][risk] = (bar_data[domain][risk] / total_studies) * 100
    
    inverted_domains = domains[::-1]
    bar_height = 0.90
    

    bottom = None
    for risk in ["High", "Moderate", "Low"]:
        values = [bar_data[domain].get(risk, 0) for domain in inverted_domains]
        ax1.barh(
            inverted_domains, 
            values, 
            left=bottom, 
            color=colors[risk], 
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
        for risk in ["High", "Moderate", "Low"]:
            width = bar_data[domain].get(risk, 0)
            if width > 0:
                ax1.text(left + width/2, i, f"{width:.0f}%", 
                        ha='center', va='center', color='black', 
                        fontsize=18, fontweight='bold')
                left += width
    

    ax1.set_xlim(0, 100)
    ax1.set_xticks([0, 20, 40, 60, 80, 100])
    ax1.set_xticklabels([0, 20, 40, 60, 80, 100], fontsize=18, fontweight='bold')
    ax1.set_yticks(range(len(inverted_domains)))
    ax1.set_yticklabels(inverted_domains, fontsize=18, fontweight='bold')
    ax1.set_xlabel("Percentage of Studies (%)", fontsize=21, fontweight='bold')
    ax1.set_ylabel("")
    ax1.set_title("Distribution of Risk-of-Bias Judgments by Domain", fontsize=25, fontweight='bold')
    ax1.grid(axis='x', linestyle='--', alpha=0.25)
    
    for y in range(len(inverted_domains)):
        ax1.axhline(y-0.5, color='lightgray', linewidth=0.8, zorder=0)
    
 
    legend_elements = [
        Line2D([0], [0], marker='s', color='w', label='Low Risk', 
              markerfacecolor=colors["Low"], markersize=17),
        Line2D([0], [0], marker='s', color='w', label='Moderate Risk', 
              markerfacecolor=colors["Moderate"], markersize=17),
        Line2D([0], [0], marker='s', color='w', label='High Risk', 
              markerfacecolor=colors["High"], markersize=17)
    ]
    legend = ax0.legend(
        handles=legend_elements,
        title="Domain Risk",
        bbox_to_anchor=(1.01, 1),
        loc='upper left',
        fontsize=21,
        title_fontsize=23,
        frameon=True,
        fancybox=True,
        edgecolor='black'
    )
    plt.setp(legend.get_title(), fontweight='bold')
    for text in legend.get_texts():
        text.set_fontweight('normal')
    
 
    valid_ext = [".png", ".pdf", ".svg", ".eps"]
    ext = os.path.splitext(output_file)[1].lower()
    if ext not in valid_ext:
        raise ValueError(f"Unsupported file format: {ext}. Use one of {valid_ext}")
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Professional combined plot saved to {output_file}")
    
    
    del bar_data

def read_input_file(file_path: str) -> pd.DataFrame:
    """Read input file"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(file_path, engine='c')
    elif ext in [".xls", ".xlsx"]:
        return pd.read_excel(file_path, engine='openpyxl')
    else:
        raise ValueError(f"Unsupported file format: {ext}. Provide a CSV or Excel file.")

def plot_nos(input_file: str, output_file: str, theme: str = "default"):
    """
    Generate a NOS traffic-light plot from input data using the updated logic.
    
    Parameters:
    -----------
    input_file : str
        Path to the input CSV or Excel file containing NOS data
    output_file : str
        Path to save the output plot (supports .png, .pdf, .svg, .eps)
    theme : str, optional
        Color theme for the plot. Options: "default", "blue", "gray", "smiley", "smiley_blue"
        
    Returns:
    --------
    None
        The plot is saved to the specified output file
    """
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)

    df = read_input_file(input_file)
    df = process_detailed_nos(df)
    professional_plot(df, output_file, theme)

if __name__ == "__main__":
    if len(sys.argv) not in [3,4]:
        print("Usage: python3 script_name.py input_file output_file.(png|pdf|svg|eps) [theme]")
        sys.exit(1)

    input_file_arg = sys.argv[1]
    output_file_arg = sys.argv[2]
    theme_arg = sys.argv[3] if len(sys.argv) == 4 else "default"

    plot_nos(input_file_arg, output_file_arg, theme_arg)