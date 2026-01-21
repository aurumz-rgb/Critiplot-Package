import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os
from matplotlib.lines import Line2D
from collections import defaultdict

def normalize_jbi_value(val):
    """Normalizes input values to 1, 0, 'Unclear', or 'Not Applicable'."""
    if pd.isna(val):
        return "Unclear"
    
    s_val = str(val).strip().lower()
    
    if s_val in ['1', 'yes', 'low']:
        return 1
    if s_val in ['0', 'no', 'high']:
        return 0
    if s_val in ['unclear', '?']:
        return "Unclear"
    if s_val in ['not applicable', 'n/a', 'na', 'not applicable']:
        return "Not Applicable"
    
    return "Unclear"

def process_jbi_case_report(df: pd.DataFrame) -> pd.DataFrame:
    if "Author,Year" not in df.columns:
        if "Author, Year" in df.columns:
            df = df.rename(columns={"Author, Year": "Author,Year"})
        elif "Author" in df.columns and "Year" in df.columns:
            df["Author,Year"] = df["Author"].astype(str) + " " + df["Year"].astype(str)
        else:
            raise ValueError("Missing required columns: 'Author,Year' or 'Author' + 'Year'")

    required_columns = [
        "Author,Year",
        "Demographics", "History", "ClinicalCondition", "Diagnostics",
        "Intervention", "PostCondition", "AdverseEvents", "Lessons",
        "Total", "Overall RoB"
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    domain_cols = [
        "Demographics", "History", "ClinicalCondition", "Diagnostics",
        "Intervention", "PostCondition", "AdverseEvents", "Lessons"
    ]
    
  
    for col in domain_cols:
        df[col] = df[col].apply(normalize_jbi_value)
        
        allowed = {1, 0, "Unclear", "Not Applicable"}
        invalid = df[~df[col].isin(allowed)]
        if not invalid.empty:
            raise ValueError(f"Column {col} contains unprocessable values after normalization.")


    df["ComputedTotal"] = df[domain_cols].apply(lambda row: sum(1 for x in row if x == 1), axis=1)
    
    mismatches = df[df["ComputedTotal"] != df["Total"]]
    if not mismatches.empty:
        print("⚠️ Warning: Total Score mismatches detected (Computed Total vs Input Total):")
        print("Note: 'Unclear' and 'Not Applicable' are treated as 0 in the sum score.")
        print(mismatches[["Author,Year", "Total", "ComputedTotal"]])

    return df

def stars_to_rob(score):
    if score == 1: return "Low"      
    if score == 0: return "High"     
    if score == "Unclear": return "Unclear"
    if score == "Not Applicable": return "Not Applicable"
    return "Unclear" 

def map_color(score, colors):
    return colors.get(stars_to_rob(score), "#BBBBBB")

def professional_jbi_plot(df: pd.DataFrame, output_file: str, theme: str = "default"):
    
    theme_options = {
        "default": {"Low":"#06923E","High":"#DC2525", "Unclear":"#F4BE3F", "Not Applicable":"#D3D3D3"},
        "blue": {"Low":"#3a83b7","High":"#084582", "Unclear":"#667CA9FF", "Not Applicable":"#838383"},
        "gray": {"Low":"#FF884DFF","High":"#5B6D80", "Unclear":"#D5617C", "Not Applicable":"#B0B0B0"},
        "smiley": {"Low":"#06923E","High":"#DC2525", "Unclear":"#F4D03F", "Not Applicable":"#898989"},
        "smiley_blue": {"Low":"#3a83b7","High":"#084582", "Unclear":"#667CA9FF", "Not Applicable":"#838383"}
    }

    if theme not in theme_options:
        raise ValueError(f"Theme {theme} not available. Choose from {list(theme_options.keys())}")
    colors = theme_options[theme]

    domains = ["Demographics", "History", "ClinicalCondition", "Diagnostics",
               "Intervention", "PostCondition", "AdverseEvents", "Lessons", "Overall RoB"]

    n_studies = len(df)
    per_study_height = 0.65   
    min_first_plot_height = 4.0
    second_plot_height = 6.5   
    gap_between_plots = 3.5
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
    
    domain_pos = {d:i for i,d in enumerate(domains)}
    author_pos = {a:i for i,a in enumerate(df["Author,Year"].tolist())}

    for y in range(len(author_pos)):
        ax0.axhline(y, color='lightgray', linewidth=0.8, zorder=0)
    ax0.axhline(-0.5, color='lightgray', linewidth=0.8, zorder=0)
    ax0.axhline(len(author_pos)-0.5, color='lightgray', linewidth=0.8, zorder=0)

    if theme.startswith("smiley"):

        symbol_map = {
            0: "☹",      
            1: "☺",       
            "Unclear": "?",
            "Not Applicable": "✖"
        }
        
        for _, row in df.iterrows():
            author = row["Author,Year"]
            y_pos = author_pos[author]
            
            for domain in domains[:-1]:
                x_pos = domain_pos[domain]
                score = row[domain]
                symbol = symbol_map.get(score, "?")
                color = colors.get(stars_to_rob(score), "#BBBBBB")
                
                ax0.text(x_pos, y_pos, symbol, fontsize=38, ha='center', va='center', 
                         color=color, fontweight='bold', zorder=1)
            
            x_pos = domain_pos["Overall RoB"]
            rob_status = row["Overall RoB"]
      
            norm_rob = normalize_jbi_value(rob_status)
            
            if norm_rob == 1 or norm_rob == "Low":
                symbol, color = "☺", colors["Low"]
            elif norm_rob == 0 or norm_rob == "High":
                symbol, color = "☹", colors["High"]
            elif norm_rob == "Unclear":
                symbol, color = "😐", colors["Unclear"]
            else:
                symbol, color = "🚫", colors["Not Applicable"]
                
            ax0.text(x_pos, y_pos, symbol, fontsize=38, ha='center', va='center', 
                     color=color, fontweight='bold', zorder=1)
        
        ax0.set_xticks(range(len(domains)))
        ax0.set_xticklabels(domains, fontsize=20, fontweight="bold", rotation=45, ha='right') 
        ax0.set_yticks(list(author_pos.values()))
        ax0.set_yticklabels(list(author_pos.keys()), fontsize=20, fontweight="bold", rotation=0) 
        ax0.set_ylim(-0.5, len(author_pos)-0.5)
        ax0.set_xlim(-0.5, len(domains)-0.5)
        ax0.set_facecolor('white')
    else:
        x_coords = []
        y_coords = []
        colors_list = []
        
        for _, row in df.iterrows():
            author = row["Author,Year"]
            y_pos = author_pos[author]
            
            for domain in domains[:-1]:
                x_coords.append(domain_pos[domain])
                y_coords.append(y_pos)
                colors_list.append(map_color(row[domain], colors))
            
            x_coords.append(domain_pos["Overall RoB"])
            y_coords.append(y_pos)

            norm_rob = normalize_jbi_value(row["Overall RoB"])
            rob_key = stars_to_rob(norm_rob)
            rob_color = colors.get(rob_key, "#BBBBBB")
            colors_list.append(rob_color)
        
        ax0.scatter(x_coords, y_coords, c=colors_list, s=1100, marker="s", zorder=1)
        ax0.set_xticks(range(len(domains)))
        ax0.set_xticklabels(domains, fontsize=20, fontweight="bold", rotation=45, ha='right')
        ax0.set_yticks(list(author_pos.values()))
        ax0.set_yticklabels(list(author_pos.keys()), fontsize=20, fontweight="bold", rotation=0)
        ax0.set_ylim(-0.5, len(author_pos)-0.5)

    ax0.set_title("JBI Case Report Traffic-Light Plot", fontsize=24, fontweight='bold',pad=12)
    ax0.set_xlabel("")
    ax0.set_ylabel("")
    ax0.grid(axis='x', linestyle='--', alpha=0.25)

    risk_counts = defaultdict(lambda: defaultdict(int))
    
    for _, row in df.iterrows():
        for domain in domains[:-1]:
            risk = stars_to_rob(row[domain])
            risk_counts[domain][risk] += 1
        
        norm_rob = normalize_jbi_value(row["Overall RoB"])
        risk_counts["Overall RoB"][stars_to_rob(norm_rob)] += 1
    
    inverted_domains = domains[::-1]
    
    categories = ["High", "Unclear", "Low", "Not Applicable"]
    counts = {cat: [] for cat in categories}
    
    for domain in inverted_domains:
        for cat in categories:
            counts[cat].append(risk_counts[domain].get(cat, 0))
    
    totals = [sum(counts[cat][i] for cat in categories) for i in range(len(inverted_domains))]
    
    high_counts = counts["High"]
    unclear_counts = counts["Unclear"]
    low_counts = counts["Low"]
    na_counts = counts["Not Applicable"]
    
    high_percent = [h / t * 100 if t > 0 else 0 for h, t in zip(high_counts, totals)]
    unclear_percent = [u / t * 100 if t > 0 else 0 for u, t in zip(unclear_counts, totals)]
    low_percent = [l / t * 100 if t > 0 else 0 for l, t in zip(low_counts, totals)]
    na_percent = [n / t * 100 if t > 0 else 0 for n, t in zip(na_counts, totals)]
    
    y_positions = range(len(inverted_domains))
    
    ax1.barh(y_positions, high_percent, color=colors["High"], edgecolor='black', label='High', height=0.85)
    ax1.barh(y_positions, unclear_percent, left=high_percent, color=colors["Unclear"], edgecolor='black', label='Unclear', height=0.85)
    ax1.barh(y_positions, low_percent, left=[h+u for h,u in zip(high_percent, unclear_percent)], color=colors["Low"], edgecolor='black', label='Low', height=0.85)

    ax1.barh(y_positions, na_percent, left=[h+u+l for h,u,l in zip(high_percent, unclear_percent, low_percent)], color=colors["Not Applicable"], edgecolor='black', label='Not Applicable', height=0.85)
    
    for i in range(len(inverted_domains)):
        if high_percent[i] > 0:
            ax1.text(high_percent[i]/2, i, f"{high_percent[i]:.0f}%", ha='center', va='center', 
                     color='black', fontsize=16, fontweight='bold')
        
        if unclear_percent[i] > 0:
            ax1.text(high_percent[i] + unclear_percent[i]/2, i, f"{unclear_percent[i]:.0f}%", ha='center', va='center', 
                     color='black', fontsize=16, fontweight='bold')
        
        if low_percent[i] > 0:
            ax1.text(high_percent[i] + unclear_percent[i] + low_percent[i]/2, i, f"{low_percent[i]:.0f}%", ha='center', va='center', 
                     color='black', fontsize=16, fontweight='bold')

        if na_percent[i] > 0:
             ax1.text(high_percent[i] + unclear_percent[i] + low_percent[i] + na_percent[i]/2, i, f"{na_percent[i]:.0f}%", ha='center', va='center', 
                     color='black', fontsize=16, fontweight='bold')
    
    ax1.set_xlim(0,100)
    ax1.set_xticks([0,20,40,60,80,100])
    ax1.set_xticklabels([0,20,40,60,80,100], fontsize=20, fontweight='bold')
    ax1.set_yticks(range(len(inverted_domains)))
    ax1.set_yticklabels(inverted_domains, fontsize=20, fontweight='bold')
    ax1.set_xlabel("Percentage of Studies (%)", fontsize=20, fontweight="bold")
    ax1.set_ylabel("")
    ax1.set_title("Distribution of Risk-of-Bias Judgments by Domain", fontsize=24, fontweight="bold")
    ax1.grid(axis='x', linestyle='--', alpha=0.25)
    
    for y in range(len(inverted_domains)):
        ax1.axhline(y-0.5, color='lightgray', linewidth=0.8, zorder=0)


    legend_elements = [
        Line2D([0],[0], marker='s', color='w', label='Low Risk (Yes)', markerfacecolor=colors["Low"], markersize=18),
        Line2D([0],[0], marker='s', color='w', label='High Risk (No)', markerfacecolor=colors["High"], markersize=18),
        Line2D([0],[0], marker='s', color='w', label='Unclear', markerfacecolor=colors["Unclear"], markersize=18),
        Line2D([0],[0], marker='s', color='w', label='Not Applicable', markerfacecolor=colors["Not Applicable"], markersize=18)
    ]
    legend = ax0.legend(
        handles=legend_elements,
        title="Domain Risk",
        bbox_to_anchor=(1.02, 1),
        loc='upper left',
        fontsize=20,
        title_fontsize=22,
        frameon=True,
        fancybox=True,
        edgecolor='black'
    )
 
    plt.setp(legend.get_title(), fontweight='bold')
    for text in legend.get_texts():
        text.set_fontweight('bold')

    valid_ext = [".png", ".pdf", ".svg", ".eps"]
    ext = os.path.splitext(output_file)[1].lower()
    if ext not in valid_ext:
        raise ValueError(f"Unsupported file format: {ext}. Use one of {valid_ext}")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"✅ Professional JBI plot saved to {output_file}")

def read_input_file(file_path: str) -> pd.DataFrame:
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".csv"]:
        return pd.read_csv(file_path, engine='c')
    elif ext in [".xls", ".xlsx"]:
        return pd.read_excel(file_path, engine='openpyxl')
    else:
        raise ValueError(f"Unsupported file format: {ext}. Provide a CSV or Excel file.")

def plot_jbi_case_report(input_file: str, output_file: str, theme: str = "default"):
    """
    Generate a JBI Case Report plot from input data.
    
    Parameters:
    -----------
    input_file : str
        Path to the input CSV or Excel file containing JBI case report data
    output_file : str
        Path where the output plot will be saved (supports .png, .pdf, .svg, .eps)
    theme : str, optional
        Plot theme, one of "default", "blue", "gray", "smiley", "smiley_blue"
        
    Returns:
    --------
    None
        The function saves the plot to the specified output file
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    df = read_input_file(input_file)
    df = process_jbi_case_report(df)
    professional_jbi_plot(df, output_file, theme)
    
if __name__ == "__main__":
    if len(sys.argv) not in [3,4]:
        print("Usage: python3 jbi_plot.py input_file output_file.(png|pdf|svg|eps) [theme]")
        sys.exit(1)

    input_file, output_file = sys.argv[1], sys.argv[2]
    theme = sys.argv[3] if len(sys.argv) == 4 else "default"

    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)

    df = read_input_file(input_file)
    df = process_jbi_case_report(df)
    professional_jbi_plot(df, output_file, theme)
    del df