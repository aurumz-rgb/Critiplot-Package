import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D



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

    numeric_cols = [
        "Demographics", "History", "ClinicalCondition", "Diagnostics",
        "Intervention", "PostCondition", "AdverseEvents", "Lessons"
    ]
    for col in numeric_cols:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise ValueError(f"Column {col} must be numeric (0 or 1).")
        if df[col].min() < 0 or df[col].max() > 1:
            raise ValueError(f"Column {col} contains invalid values (0 or 1 allowed).")

    df["ComputedTotal"] = df[numeric_cols].sum(axis=1)
    mismatches = df[df["ComputedTotal"] != df["Total"]]
    if not mismatches.empty:
        print("⚠️ Warning: Total Score mismatches detected:")
        print(mismatches[["Author,Year", "Total", "ComputedTotal"]])

    return df



def stars_to_rob(score):
    return "Low" if score == 1 else "High"

def map_color(score, colors):
    return colors.get(stars_to_rob(score), "#BBBBBB")



def professional_jbi_plot(df: pd.DataFrame, output_file: str, theme: str = "default"):
    theme_options = {
        "default": {"Low":"#06923E","High":"#DC2525"},
        "blue": {"Low":"#3a83b7","High":"#084582"},
        "gray": {"Low":"#FF884DFF","High":"#5B6D80"},
        "smiley": {"Low":"#06923E","High":"#DC2525"},
        "smiley_blue": {"Low":"#3a83b7","High":"#084582"}
    }

    if theme not in theme_options:
        raise ValueError(f"Theme {theme} not available. Choose from {list(theme_options.keys())}")
    colors = theme_options[theme]

    domains = ["Demographics", "History", "ClinicalCondition", "Diagnostics",
               "Intervention", "PostCondition", "AdverseEvents", "Lessons", "Overall RoB"]

    # Fixed 
    n_studies = len(df)
    per_study_height = 0.5      
    min_first_plot_height = 4.0
    second_plot_height = 4.5    
    gap_between_plots = 3.0   
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
    
    plot_data = []
    for _, row in df.iterrows():
        for domain in domains[:-1]: 
            plot_data.append({
                "Author,Year": row["Author,Year"],
                "Domain": domain,
                "Score": row[domain],
                "Type": "score"
            })

        plot_data.append({
            "Author,Year": row["Author,Year"],
            "Domain": "Overall RoB",
            "Score": row["Overall RoB"],
            "Type": "rob"
        })
    
    plot_df = pd.DataFrame(plot_data)

    domain_pos = {d:i for i,d in enumerate(domains)}
    author_pos = {a:i for i,a in enumerate(df["Author,Year"].tolist())}

    for y in range(len(author_pos)):
        ax0.axhline(y, color='lightgray', linewidth=0.8, zorder=0)
    ax0.axhline(-0.5, color='lightgray', linewidth=0.8, zorder=0)
    ax0.axhline(len(author_pos)-0.5, color='lightgray', linewidth=0.8, zorder=0)

    if theme.startswith("smiley"):
        def score_to_symbol(score, domain):
            if domain == "Overall RoB":
                return "☺" if score == "Low" else "☹"
            return "☺" if score == 1 else "☹"
        
        plot_df["Symbol"] = plot_df.apply(lambda x: score_to_symbol(x["Score"], x["Domain"]), axis=1)
        plot_df["Color"] = plot_df.apply(
            lambda x: colors.get(x["Score"], "#BBBBBB") if x["Domain"] == "Overall RoB" 
            else colors[stars_to_rob(x["Score"])], 
            axis=1
        )
        
        for i, row in plot_df.iterrows():
            ax0.text(domain_pos[row["Domain"]], author_pos[row["Author,Year"]],
                     row["Symbol"], fontsize=30, ha='center', va='center', color=row["Color"], fontweight='bold', zorder=1)
        ax0.set_xticks(range(len(domains)))
        ax0.set_xticklabels(domains, fontsize=14, fontweight="bold", rotation=45, ha='right')
        ax0.set_yticks(list(author_pos.values()))
        ax0.set_yticklabels(list(author_pos.keys()), fontsize=11, fontweight="bold", rotation=0)

        ax0.set_ylim(-0.5, len(author_pos)-0.5)
        ax0.set_xlim(-0.5, len(domains)-0.5)
        ax0.set_facecolor('white')
    else:
        plot_df["Color"] = plot_df.apply(
            lambda x: colors.get(x["Score"], "#BBBBBB") if x["Domain"] == "Overall RoB" 
            else map_color(x["Score"], colors), 
            axis=1
        )
        palette = {c:c for c in plot_df["Color"].unique()}
        sns.scatterplot(
            data=plot_df,
            x="Domain",
            y="Author,Year",
            hue="Color",
            palette=palette,
            s=800,
            marker="s",
            legend=False,
            ax=ax0
        )
        ax0.set_xticks(range(len(domains)))
        ax0.set_xticklabels(domains, fontsize=14, fontweight="bold", rotation=45, ha='right')
        ax0.set_yticks(list(author_pos.values()))
        ax0.set_yticklabels(list(author_pos.keys()), fontsize=11, fontweight="bold", rotation=0)

        ax0.set_ylim(-0.5, len(author_pos)-0.5)

    ax0.set_title("JBI Case Report Traffic-Light Plot", fontsize=18, fontweight="bold")
    ax0.set_xlabel("")
    ax0.set_ylabel("")
    ax0.grid(axis='x', linestyle='--', alpha=0.25)

    stacked_data = []
    for _, row in df.iterrows():
        for domain in domains[:-1]:  
            risk = stars_to_rob(row[domain])
            stacked_data.append({
                "Domain": domain,
                "RoB": risk
            })

        stacked_data.append({
            "Domain": "Overall RoB",
            "RoB": row["Overall RoB"]
        })
    
    stacked_df = pd.DataFrame(stacked_data)
    
    counts = stacked_df.groupby(["Domain", "RoB"]).size().unstack(fill_value=0)
    
    for risk in ["Low", "High"]:
        if risk not in counts.columns:
            counts[risk] = 0
    
    counts_percent = counts.div(counts.sum(axis=1), axis=0) * 100

    inverted_domains = domains[::-1]
    counts_percent = counts_percent.reindex(inverted_domains)
    
    bottom = None
    for rob in ["High", "Low"]:
        if rob in counts_percent.columns:
            ax1.barh(counts_percent.index, counts_percent[rob], left=bottom, color=colors[rob], edgecolor='black', label=rob)
            bottom = counts_percent[rob] if bottom is None else bottom + counts_percent[rob]

    for i, domain in enumerate(counts_percent.index):
        left = 0
        for rob in ["High", "Low"]:
            if rob in counts_percent.columns:
                width = counts_percent.loc[domain, rob]
                if width > 0:
                    ax1.text(left + width/2, i, f"{width:.0f}%", ha='center', va='center', 
                             color='black', fontsize=14, fontweight='bold')
                    left += width

    ax1.set_xlim(0,100)
    ax1.set_xticks([0,20,40,60,80,100])
    ax1.set_xticklabels([0,20,40,60,80,100], fontsize=14, fontweight='bold')  
    ax1.set_yticks(range(len(inverted_domains)))
    ax1.set_yticklabels(inverted_domains, fontsize=14, fontweight='bold') 
    ax1.set_xlabel("Percentage of Studies (%)", fontsize=16, fontweight="bold") 
    ax1.set_ylabel("")
    ax1.set_title("Distribution of Risk-of-Bias Judgments by Domain", fontsize=18, fontweight="bold")
    ax1.grid(axis='x', linestyle='--', alpha=0.25)
    
    for y in range(len(inverted_domains)):
        ax1.axhline(y-0.5, color='lightgray', linewidth=0.8, zorder=0)

    legend_elements = [
        Line2D([0],[0], marker='s', color='w', label='Low Risk', markerfacecolor=colors["Low"], markersize=12),
        Line2D([0],[0], marker='s', color='w', label='High Risk', markerfacecolor=colors["High"], markersize=12)
    ]
    legend = ax0.legend(
        handles=legend_elements,
        title="Domain Risk",
        bbox_to_anchor=(1.02, 1),
        loc='upper left',
        fontsize=14,
        title_fontsize=16,
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
    plt.close()
    print(f"✅ Professional JBI plot saved to {output_file}")



def read_input_file(file_path: str) -> pd.DataFrame:
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".csv"]:
        return pd.read_csv(file_path)
    elif ext in [".xls", ".xlsx"]:
        return pd.read_excel(file_path)
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