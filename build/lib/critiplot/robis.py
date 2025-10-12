import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D


# Process ROBIS table
def process_robis(df: pd.DataFrame) -> pd.DataFrame:
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


# Smiley symbol mapper
def risk_to_symbol(risk: str) -> str:
    if risk == "Low":
        return "☺"
    elif risk == "Unclear":
        return "😐"
    elif risk == "High":
        return "☹"
    return "?"


# Standardize risk categories
def standardize_risk(risk):
    risk = str(risk).strip().lower()
    if risk in ['high', 'h']:
        return 'High'
    elif risk in ['unclear', 'uncertain', 'u']:
        return 'Unclear'
    elif risk in ['low', 'l']:
        return 'Low'
    else:
        return 'Unclear'  # Default to Unclear for any unrecognized values


# Helper: Read CSV or Excel
def read_input_file(file_path: str) -> pd.DataFrame:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(file_path)
    elif ext in [".xls", ".xlsx"]:
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Provide a CSV or Excel file.")


# Professional ROBIS plot
def professional_robis_plot(df: pd.DataFrame, output_file: str, theme: str = "default"):
    theme_options = {
        "default": {"Low":"#06923E","Unclear":"#FFD93D","High":"#DC2525"},
        "blue": {"Low":"#3a83b7","Unclear":"#7fb2e6","High":"#084582"},
        "gray": {"Low":"#7f7f7f","Unclear":"#b0b0b0","High":"#3b3b3b"},
        "smiley": {"Low":"#06923E","Unclear":"#FFD93D","High":"#DC2525"},
        "smiley_blue": {"Low":"#3a83b7","Unclear":"#7fb2e6","High":"#084582"}
    }

    if theme not in theme_options:
        raise ValueError(f"Theme {theme} not available. Choose from {list(theme_options.keys())}")
    colors = theme_options[theme]

    domains = ["Study Eligibility","Identification & Selection","Data Collection","Synthesis & Findings","Overall Risk"]

    fig_height = max(6, 0.7*len(df) + 5)
    fig = plt.figure(figsize=(18, fig_height), constrained_layout=True)
    gs = GridSpec(2, 1, height_ratios=[len(df)*0.7, 1.5], hspace=0.35, figure=fig)

   
    # Traffic-Light / Smiley Plot
    ax0 = fig.add_subplot(gs[0])
    
    # Create a combined dataframe for all domains including Overall Risk
    plot_data = []
    for _, row in df.iterrows():
        for domain in domains:
            plot_data.append({
                "Review": row["Review"],
                "Domain": domain,
                "Risk": row[domain]
            })
    
    plot_df = pd.DataFrame(plot_data)
    # Standardize risk categories in the plot data
    plot_df["Risk"] = plot_df["Risk"].apply(standardize_risk)

    domain_pos = {d:i for i,d in enumerate(domains)}
    review_pos = {a:i for i,a in enumerate(df["Review"].tolist())}

    
    for y in range(len(review_pos)+1):
        ax0.axhline(y-0.5, color='lightgray', linewidth=0.8, zorder=0)

    if theme.startswith("smiley"):
        plot_df["Symbol"] = plot_df["Risk"].apply(risk_to_symbol)
        plot_df["Color"] = plot_df["Risk"].apply(lambda x: colors.get(x, "#BBBBBB"))
        for _, row in plot_df.iterrows():
            ax0.text(domain_pos[row["Domain"]], review_pos[row["Review"]],
                     row["Symbol"], fontsize=24, ha='center', va='center',
                     color=row["Color"], fontweight="bold", zorder=1)
        ax0.set_xticks(range(len(domains)))
        ax0.set_xticklabels(domains, fontsize=12, fontweight="bold")
        ax0.set_yticks(list(review_pos.values()))
        ax0.set_yticklabels(list(review_pos.keys()), fontsize=11, fontweight="bold")
        ax0.set_ylim(-0.5, len(review_pos)-0.5)
        ax0.set_xlim(-0.5, len(domains)-0.5)
        ax0.set_facecolor('white')
    else:
        plot_df["Color"] = plot_df["Risk"].apply(lambda x: colors.get(x, "#BBBBBB"))
        palette = {c:c for c in plot_df["Color"].unique()}
        sns.scatterplot(
            data=plot_df,
            x="Domain",
            y="Review",
            hue="Color",
            palette=palette,
            s=350,
            marker="s",
            legend=False,
            ax=ax0
        )
        ax0.tick_params(axis='y', labelsize=11)
        for label in ax0.get_xticklabels():
            label.set_fontweight("bold")
        for label in ax0.get_yticklabels():
            label.set_fontweight("bold")

    ax0.set_title("ROBIS Traffic-Light Plot", fontsize=18, fontweight="bold")
    ax0.set_xlabel("")
    ax0.set_ylabel("")
    ax0.grid(axis='x', linestyle='--', alpha=0.25)


    # Distribution Bar Plot
    ax1 = fig.add_subplot(gs[1])
    
    # Create a properly structured dataframe for the stacked bar plot
    stacked_data = []
    
    # Add data for each domain
    for _, row in df.iterrows():
        for domain in domains:
            risk = standardize_risk(row[domain])
            stacked_data.append({
                "Domain": domain,
                "Risk": risk
            })
    
    stacked_df = pd.DataFrame(stacked_data)
    
    # Count occurrences of each risk category per domain
    counts = stacked_df.groupby(["Domain", "Risk"]).size().unstack(fill_value=0)
    
    # Ensure all risk categories are present
    for risk in ["Low", "Unclear", "High"]:
        if risk not in counts.columns:
            counts[risk] = 0
    
    # Calculate percentages
    counts_percent = counts.div(counts.sum(axis=1), axis=0) * 100
    
    # Reorder the counts_percent to have the domains in the same order as the first plot
    counts_percent = counts_percent.reindex(domains)
    
    bottom = None
    for rob in ["High", "Unclear", "Low"]:
        if rob in counts_percent.columns:
            ax1.barh(counts_percent.index, counts_percent[rob], left=bottom,
                     color=colors.get(rob, "#BBBBBB"), edgecolor='black', label=rob)
            bottom = counts_percent[rob] if bottom is None else bottom + counts_percent[rob]

    for i, domain in enumerate(counts_percent.index):
        left = 0
        for rob in ["High", "Unclear", "Low"]:
            if rob in counts_percent.columns:
                width = counts_percent.loc[domain, rob]
                if width > 0:
                    ax1.text(left + width/2, i, f"{width:.0f}%", ha='center', va='center',
                             color='black', fontsize=10, fontweight="bold")
                    left += width

    ax1.set_xlim(0,100)
    ax1.set_xlabel("Percentage of Reviews (%)", fontsize=13, fontweight="bold")
    ax1.set_ylabel("")
    ax1.set_title("Distribution of Risk-of-Bias Judgments by Domain", fontsize=18, fontweight="bold")
    ax1.grid(axis='x', linestyle='--', alpha=0.25)
    
    # Update the y-axis to use domains in the correct order
    ax1.set_yticks(range(len(domains)))
    ax1.set_yticklabels(domains, fontsize=12, fontweight="bold")
    
    for label in ax1.get_yticklabels():
        label.set_fontweight("bold")
    for label in ax1.get_xticklabels():
        label.set_fontweight("bold")

    for y in range(len(domains)):
        ax1.axhline(y-0.5, color='lightgray', linewidth=0.8, zorder=0)

    legend_elements = [
        Line2D([0],[0], marker='s', color='w', label='Low Risk', markerfacecolor=colors.get("Low", "#BBBBBB"), markersize=20),
        Line2D([0],[0], marker='s', color='w', label='Unclear Risk', markerfacecolor=colors.get("Unclear", "#BBBBBB"), markersize=20),
        Line2D([0],[0], marker='s', color='w', label='High Risk', markerfacecolor=colors.get("High", "#BBBBBB"), markersize=20)
    ]
    legend = ax0.legend(handles=legend_elements, title="Domain Risk",
                        bbox_to_anchor=(1.15, 1), loc='upper left',
                        fontsize=14, title_fontsize=16)
    plt.setp(legend.get_texts(), fontweight="bold")
    plt.setp(legend.get_title(), fontweight="bold")

    # Save file
    valid_ext = [".png", ".pdf", ".svg", ".eps"]
    ext = os.path.splitext(output_file)[1].lower()
    if ext not in valid_ext:
        raise ValueError(f"Unsupported file format: {ext}. Use one of {valid_ext}")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ ROBIS professional plot saved to {output_file}")


# Public function for the module
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