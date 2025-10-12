import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D


# Processing the detailed NOS table
def process_detailed_nos(df: pd.DataFrame) -> pd.DataFrame:
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


# Map stars to risk categories
def stars_to_rob(stars, domain):
    if domain == "Selection":
        return "Low" if stars >= 3 else "Moderate" if stars == 2 else "High"
    elif domain == "Comparability":
        return "Low" if stars == 2 else "Moderate" if stars == 1 else "High"
    elif domain == "Outcome/Exposure":
        return "Low" if stars == 3 else "Moderate" if stars == 2 else "High"
    return "High"

def map_color(stars, domain, colors):
    risk = stars_to_rob(stars, domain)
    return colors.get(risk, "#BBBBBB")


# Professional combined plot
def professional_plot(df: pd.DataFrame, output_file: str, theme: str = "default"):
    theme_options = {
        "default": {"Low":"#2E7D32", "Moderate":"#F9A825", "High":"#C62828"},
        "blue": {"Low":"#3a83b7","Moderate":"#bdcfe7","High":"#084582"},
        "gray": {"Low":"#7f7f7f","Moderate":"#b0b0b0","High":"#3b3b3b"},
        "smiley": {"Low":"#2E7D32", "Moderate":"#F9A825", "High":"#C62828"},
        "smiley_blue": {"Low":"#3a83b7","Moderate":"#7fb2e6","High":"#084582"}
    }

    if theme not in theme_options:
        raise ValueError(f"Theme {theme} not available. Choose from {list(theme_options.keys())}")
    colors = theme_options[theme]

    domains = ["Selection","Comparability","Outcome/Exposure","Overall RoB"]

    fig_height = max(6, 0.7*len(df) + 5)
    fig = plt.figure(figsize=(18, fig_height))
    gs = GridSpec(2, 1, height_ratios=[len(df)*0.7, 1.5], hspace=0.4)

   
    # Traffic-Light / Smiley Plot
    ax0 = fig.add_subplot(gs[0])
    
    # Create a combined dataframe for all domains including Overall RoB
    plot_data = []
    for _, row in df.iterrows():
        for domain in domains[:-1]:  # For the first three domains
            plot_data.append({
                "Author, Year": row["Author, Year"],
                "Domain": domain,
                "Value": row[domain],
                "Type": "stars"
            })
        # Add Overall RoB
        plot_data.append({
            "Author, Year": row["Author, Year"],
            "Domain": "Overall RoB",
            "Value": row["Overall RoB"],
            "Type": "rob"
        })
    
    plot_df = pd.DataFrame(plot_data)

    domain_pos = {d:i for i,d in enumerate(domains)}
    author_pos = {a:i for i,a in enumerate(df["Author, Year"].tolist())}

    for y in range(len(author_pos)+1):
        ax0.axhline(y-0.5, color='lightgray', linewidth=0.8, zorder=0)

    if theme.startswith("smiley"):
        def stars_to_symbol(stars, domain):
            if domain == "Overall RoB":
                return {"Low":"☺","Moderate":"😐","High":"☹"}.get(stars,"?")
            risk = stars_to_rob(stars, domain)
            return {"Low":"☺","Moderate":"😐","High":"☹"}.get(risk,"?")
        
        plot_df["Symbol"] = plot_df.apply(lambda x: stars_to_symbol(x["Value"], x["Domain"]), axis=1)
        plot_df["Color"] = plot_df.apply(
            lambda x: colors.get(x["Value"], "#BBBBBB") if x["Domain"] == "Overall RoB" 
            else colors[stars_to_rob(x["Value"], x["Domain"])], 
            axis=1
        )

        for i, row in plot_df.iterrows():
            ax0.text(domain_pos[row["Domain"]], author_pos[row["Author, Year"]],
                     row["Symbol"], fontsize=24, ha='center', va='center', color=row["Color"], fontweight='bold', zorder=1)

        ax0.set_xticks(range(len(domains)))
        ax0.set_xticklabels(domains, fontsize=14, fontweight="bold")
        ax0.set_yticks(list(author_pos.values()))
        ax0.set_yticklabels(list(author_pos.keys()), fontsize=11, fontweight="bold", rotation=0)
        ax0.set_ylim(-0.5, len(author_pos)-0.5)
        ax0.set_xlim(-0.5, len(domains)-0.5)
        ax0.set_facecolor('white')

    else:
        plot_df["Color"] = plot_df.apply(
            lambda x: colors.get(x["Value"], "#BBBBBB") if x["Domain"] == "Overall RoB" 
            else map_color(x["Value"], x["Domain"], colors), 
            axis=1
        )
        palette = {c:c for c in plot_df["Color"].unique()}
        sns.scatterplot(
            data=plot_df,
            x="Domain",
            y="Author, Year",
            hue="Color",
            palette=palette,
            s=350,
            marker="s",
            legend=False,
            ax=ax0
        )
        ax0.set_xticks(range(len(domains)))
        ax0.set_xticklabels(domains, fontsize=14, fontweight="bold")
        ax0.set_yticks(list(author_pos.values()))
        ax0.set_yticklabels(list(author_pos.keys()), fontsize=11, fontweight="bold", rotation=0)

    ax0.set_title("NOS Traffic-Light Plot", fontsize=18, fontweight="bold")
    ax0.set_xlabel("")
    ax0.set_ylabel("")
    ax0.grid(axis='x', linestyle='--', alpha=0.25)

    
    # Weighted Horizontal Stacked Bar Plot
    ax1 = fig.add_subplot(gs[1])
    ax1.set_position([0.12, ax1.get_position().y0, 0.75, ax1.get_position().height])

    # Create a properly structured dataframe for the stacked bar plot
    stacked_data = []
    for _, row in df.iterrows():
        # Add data for each domain
        for domain in domains[:-1]:  # For the first three domains
            risk = stars_to_rob(row[domain], domain)
            stacked_data.append({
                "Domain": domain,
                "RoB": risk
            })
        # Add Overall RoB
        stacked_data.append({
            "Domain": "Overall RoB",
            "RoB": row["Overall RoB"]
        })
    
    stacked_df = pd.DataFrame(stacked_data)
    
    # Count occurrences of each risk category per domain
    counts = stacked_df.groupby(["Domain", "RoB"]).size().unstack(fill_value=0)
    
    # Ensure all risk categories are present
    for risk in ["Low", "Moderate", "High"]:
        if risk not in counts.columns:
            counts[risk] = 0
    
    # Calculate percentages
    counts_percent = counts.div(counts.sum(axis=1), axis=0) * 100
    
    # Reorder domains to match the first plot
    counts_percent = counts_percent.reindex(domains)
    
    bottom = None
    for rob in ["High", "Moderate", "Low"]:
        if rob in counts_percent.columns:
            ax1.barh(counts_percent.index, counts_percent[rob], left=bottom, color=colors[rob], edgecolor='black', label=rob)
            bottom = counts_percent[rob] if bottom is None else bottom + counts_percent[rob]

    for i, domain in enumerate(counts_percent.index):
        left = 0
        for rob in ["High", "Moderate", "Low"]:
            if rob in counts_percent.columns:
                width = counts_percent.loc[domain, rob]
                if width > 0:
                    ax1.text(left + width/2, i, f"{width:.0f}%", ha='center', va='center', color='black', fontsize=12, fontweight='bold')
                    left += width

    ax1.set_xlim(0,100)
    ax1.set_xticks([0,20,40,60,80,100])
    ax1.set_xticklabels([0,20,40,60,80,100], fontsize=12, fontweight='bold')
    ax1.set_yticks(range(len(domains)))
    ax1.set_yticklabels(domains, fontsize=12, fontweight='bold')

    ax1.set_xlabel("Percentage of Studies (%)", fontsize=14, fontweight='bold')
    ax1.set_ylabel("")
    ax1.set_title("Distribution of Risk-of-Bias Judgments by Domain", fontsize=18, fontweight='bold')
    ax1.grid(axis='x', linestyle='--', alpha=0.25)
    for y in range(len(domains)):
        ax1.axhline(y-0.5, color='lightgray', linewidth=0.8, zorder=0)


    # Clean Legend 
    legend_elements = [
        Line2D([0],[0], marker='s', color='w', label='Low Risk', markerfacecolor=colors["Low"], markersize=12),
        Line2D([0],[0], marker='s', color='w', label='Moderate Risk', markerfacecolor=colors["Moderate"], markersize=12),
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


    # Save figure
    valid_ext = [".png", ".pdf", ".svg", ".eps"]
    ext = os.path.splitext(output_file)[1].lower()
    if ext not in valid_ext:
        raise ValueError(f"Unsupported file format: {ext}. Use one of {valid_ext}")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Professional combined plot saved to {output_file}")


# Helper: Read CSV or Excel
def read_input_file(file_path: str) -> pd.DataFrame:
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".csv"]:
        return pd.read_csv(file_path)
    elif ext in [".xls", ".xlsx"]:
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Provide a CSV or Excel file.")


# Public function
def plot_nos(input_file: str, output_file: str, theme: str = "default"):
    """
    Generate a NOS traffic-light plot from input data.
    
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
    df = read_input_file(input_file)
    df = process_detailed_nos(df)
    professional_plot(df, output_file, theme)