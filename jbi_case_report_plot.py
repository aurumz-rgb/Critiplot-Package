import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D

# -----------------------------
# Processing JBI Case Report
# -----------------------------
def process_jbi_case_report(df: pd.DataFrame) -> pd.DataFrame:
    # Handle flexible Author/Year columns
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

# -----------------------------
# Map numeric to risk categories
# -----------------------------
def stars_to_rob(score):
    return "Low" if score == 1 else "High"

def map_color(score, colors):
    return colors.get(stars_to_rob(score), "#BBBBBB")

# -----------------------------
# Professional JBI plot
# -----------------------------
def professional_jbi_plot(df: pd.DataFrame, output_file: str, theme: str = "default"):
    theme_options = {
        "default": {"Low":"#06923E","High":"#DC2525"},
        "blue": {"Low":"#3a83b7","High":"#084582"},
        "gray": {"Low":"#7f7f7f","High":"#3b3b3b"},
        "smiley": {"Low":"#06923E","High":"#DC2525"},
        "smiley_blue": {"Low":"#3a83b7","High":"#084582"}
    }

    if theme not in theme_options:
        raise ValueError(f"Theme {theme} not available. Choose from {list(theme_options.keys())}")
    colors = theme_options[theme]

    domains = ["Demographics", "History", "ClinicalCondition", "Diagnostics",
               "Intervention", "PostCondition", "AdverseEvents", "Lessons"]

    fig_height = max(6, 0.7*len(df) + 5)
    fig = plt.figure(figsize=(18, fig_height))
    gs = GridSpec(2, 1, height_ratios=[len(df)*0.7, 1.5], hspace=0.4)

    # -----------------------------
    # Traffic-Light / Smiley Plot
    # -----------------------------
    ax0 = fig.add_subplot(gs[0])
    plot_df = df.melt(id_vars=["Author,Year"], 
                      value_vars=domains,
                      var_name="Domain", value_name="Score")

    domain_pos = {d:i for i,d in enumerate(domains)}
    author_pos = {a:i for i,a in enumerate(df["Author,Year"].tolist())}

    for y in range(len(author_pos)+1):
        ax0.axhline(y-0.5, color='lightgray', linewidth=0.8, zorder=0)

    if theme.startswith("smiley"):
        def score_to_symbol(score):
            return "☺" if score == 1 else "☹"
        plot_df["Symbol"] = plot_df["Score"].apply(score_to_symbol)
        plot_df["Color"] = plot_df["Score"].apply(lambda x: colors[stars_to_rob(x)])
        for i, row in plot_df.iterrows():
            ax0.text(domain_pos[row["Domain"]], author_pos[row["Author,Year"]],
                     row["Symbol"], fontsize=24, ha='center', va='center', color=row["Color"], fontweight='bold', zorder=1)
        ax0.set_xticks(range(len(domains)))
        ax0.set_xticklabels(domains, fontsize=14, fontweight="bold")
        ax0.set_yticks(list(author_pos.values()))
        ax0.set_yticklabels(list(author_pos.keys()), fontsize=11, fontweight="bold", rotation=0)
        ax0.set_ylim(-0.5, len(author_pos)-0.5)
        ax0.set_xlim(-0.5, len(domains)-0.5)
        ax0.set_facecolor('white')
    else:
        plot_df["Color"] = plot_df["Score"].apply(lambda x: map_color(x, colors))
        palette = {c:c for c in plot_df["Color"].unique()}
        sns.scatterplot(
            data=plot_df,
            x="Domain",
            y="Author,Year",
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

    ax0.set_title("JBI Case Report Traffic-Light Plot", fontsize=18, fontweight="bold")
    ax0.set_xlabel("")
    ax0.set_ylabel("")
    ax0.grid(axis='x', linestyle='--', alpha=0.25)

    # -----------------------------
    # Horizontal Stacked Bar Plot
    # -----------------------------
    ax1 = fig.add_subplot(gs[1])
    stacked_df = pd.DataFrame()
    for domain in domains:
        temp = df[[domain]].copy()
        temp["Domain"] = domain
        temp["RoB"] = temp[domain].apply(stars_to_rob)
        stacked_df = pd.concat([stacked_df, temp[["Domain","RoB"]]], axis=0)

    counts = stacked_df.groupby(["Domain","RoB"]).size().unstack(fill_value=0)
    counts_percent = counts.div(counts.sum(axis=1), axis=0) * 100

    bottom = None
    for rob in ["High","Low"]:
        if rob in counts_percent.columns:
            ax1.barh(counts_percent.index, counts_percent[rob], left=bottom, color=colors[rob], edgecolor='black', label=rob)
            bottom = counts_percent[rob] if bottom is None else bottom + counts_percent[rob]

    for i, domain in enumerate(counts_percent.index):
        left = 0
        for rob in ["High","Low"]:
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
    ax1.set_xlabel("Percentage of Studies (%)", fontsize=14, fontweight="bold")
    ax1.set_ylabel("")
    ax1.set_title("Distribution of Risk-of-Bias Judgments by Domain", fontsize=18, fontweight="bold")
    ax1.grid(axis='x', linestyle='--', alpha=0.25)
    for y in range(len(domains)):
        ax1.axhline(y-0.5, color='lightgray', linewidth=0.8, zorder=0)

    # -----------------------------
    # Legend
    # -----------------------------
    legend_elements = [
        Line2D([0],[0], marker='s', color='w', label='Low Risk', markerfacecolor=colors["Low"], markersize=12),
        Line2D([0],[0], marker='s', color='w', label='High Risk', markerfacecolor=colors["High"], markersize=12)
    ]
    ax0.legend(
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

    # -----------------------------
    # Save figure
    # -----------------------------
    valid_ext = [".png", ".pdf", ".svg", ".eps"]
    ext = os.path.splitext(output_file)[1].lower()
    if ext not in valid_ext:
        raise ValueError(f"Unsupported file format: {ext}. Use one of {valid_ext}")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Professional JBI plot saved to {output_file}")

# -----------------------------
# Helper: Read CSV or Excel
# -----------------------------
def read_input_file(file_path: str) -> pd.DataFrame:
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".csv"]:
        return pd.read_csv(file_path)
    elif ext in [".xls", ".xlsx"]:
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Provide a CSV or Excel file.")

# -----------------------------
# Main
# -----------------------------
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
