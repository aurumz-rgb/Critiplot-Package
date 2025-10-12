import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Patch

def _process_grade(df: pd.DataFrame) -> pd.DataFrame:
    """Process GRADE data for plotting.
    
    Args:
        df: Input DataFrame with GRADE assessment data
        
    Returns:
        Processed DataFrame ready for plotting
    """
    column_map = {
        "Other Considerations": "Publication Bias"
    }
    df = df.rename(columns=column_map)

    
    if "Publication Bias" in df.columns:
        df["Publication Bias"] = df["Publication Bias"].fillna("None")

    required_columns = ["Outcome","Study","Risk of Bias","Inconsistency","Indirectness","Imprecision","Publication Bias","Overall Certainty"]
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    
    df["Outcome_Display"] = df["Outcome"] + " (" + df["Study"] + ")"
    return df

def _map_color(certainty, colors):
    """Map certainty level to color.
    
    Args:
        certainty: Certainty level (e.g., "High", "Moderate", etc.)
        colors: Dictionary mapping certainty levels to colors
        
    Returns:
        Color hex code for the given certainty level
    """
    return colors.get(certainty, "grey")

def _read_input_file(input_file: str) -> pd.DataFrame:
    """Read input file (CSV or Excel) into DataFrame.
    
    Args:
        input_file: Path to input file
        
    Returns:
        DataFrame with the contents of the input file
        
    Raises:
        ValueError: If file format is not supported
    """
    if input_file.endswith(".csv"):
        return pd.read_csv(input_file)
    elif input_file.endswith(".xlsx") or input_file.endswith(".xls"):
        return pd.read_excel(input_file)
    else:
        raise ValueError("Unsupported file format. Please use .csv or .xlsx/.xls")

def _grade_plot(df: pd.DataFrame, output_file: str, theme="default"):
    """Generate GRADE traffic-light plot and save to file.
    
    Args:
        df: Processed DataFrame with GRADE assessment data
        output_file: Path to save the output plot
        theme: Color theme to use for the plot (default: "default")
    """
    theme_options = {
        "green": {  
            "High":"#276B37",
            "Moderate":"#56AF29",
            "Low":"#3376AD",
            "Very Low":"#7D7D7D",
            "None":"#B5B5B5"
        },
        "default": {  
            "High":"#3A896F",
            "Moderate":"#AEBF2B",
            "Low":"#FFBB00",
            "Very Low":"#B42222",
            "None":"#818181"
        },
        "blue": {  
            "High":"#006699",
            "Moderate":"#3399CC",
            "Low":"#FFCC66",
            "Very Low":"#CC3333",
            "None":"#B0B0B0"
        }
    }

    if theme not in theme_options:
        raise ValueError("Invalid theme.")
    colors = theme_options[theme]

    fig_height = max(6, 0.7*len(df) + 5)
    fig = plt.figure(figsize=(18, fig_height))
    gs = GridSpec(2,1, height_ratios=[len(df)*0.7, 1.5], hspace=0.4)

    # Traffic-light plot
    ax0 = fig.add_subplot(gs[0])
    domains = ["Risk of Bias","Inconsistency","Indirectness","Imprecision","Publication Bias", "Overall Certainty"]
    plot_df = df.melt(id_vars=["Outcome_Display"], value_vars=domains, var_name="Domain", value_name="Certainty")
    
    plot_df["Color"] = plot_df["Certainty"].apply(lambda x: _map_color(x, colors))
    sns.scatterplot(data=plot_df, x="Domain", y="Outcome_Display",
                    hue="Color", palette={c:c for c in plot_df["Color"].unique()},
                    s=350, marker="s", legend=False, ax=ax0)
    outcome_pos = {out:i for i,out in enumerate(df["Outcome_Display"].tolist())}

    for y in range(len(outcome_pos)+1):
        ax0.axhline(y-0.5, color='lightgray', linewidth=0.8, zorder=0)

    ax0.set_xticks(range(len(domains)))
    ax0.set_xticklabels(domains, fontsize=12, fontweight="bold")
    ax0.set_yticks(list(outcome_pos.values()))
    ax0.set_yticklabels(list(outcome_pos.keys()), fontsize=10, fontweight="bold")
    ax0.set_ylim(-0.5, len(outcome_pos)-0.5)
    ax0.set_xlim(-0.5, len(domains)-0.5)
    ax0.set_facecolor("white")

    ax0.set_title("GRADE Traffic-Light Plot", fontsize=18, fontweight="bold")
    ax0.set_xlabel("GRADE Domains", fontsize=12, fontweight="bold")
    ax0.set_ylabel("", fontsize=12, fontweight="bold")
    ax0.tick_params(axis='y', labelsize=10)

    legend_elements = [Patch(facecolor=colors[c], edgecolor='black', label=c) for c in ["High","Moderate","Low","Very Low","None"]]
    leg = ax0.legend(handles=legend_elements, title="Certainty", bbox_to_anchor=(1.02,1), loc='upper left', frameon=True, borderpad=1)
    plt.setp(leg.get_texts(), fontweight="bold")
    plt.setp(leg.get_title(), fontweight="bold")

   
    ax1 = fig.add_subplot(gs[1])
    
    # Create a new DataFrame that includes Overall Certainty
    bar_df = pd.concat([
        plot_df,  # Original domains
        pd.DataFrame({
            "Domain": "Overall Certainty",
            "Certainty": df["Overall Certainty"]
        })
    ], ignore_index=True)
    
    counts = bar_df.groupby(["Domain","Certainty"]).size().unstack(fill_value=0)
    counts_percent = counts.div(counts.sum(axis=1), axis=0)*100
    bottom=None

    for cert in ["Very Low","Low","Moderate","High","None"]:
        if cert in counts_percent.columns:
            ax1.barh(counts_percent.index, counts_percent[cert], left=bottom,
                     color=colors[cert], edgecolor="black", linewidth=1.5, label=cert)
            
            for i, val in enumerate(counts_percent[cert]):
                if val > 0:
                    left_val = 0 if bottom is None else bottom.iloc[i]
                    ax1.text(left_val + val/2, i, f"{val:.1f}%", va='center', ha='center', fontsize=10, color='black', fontweight="bold")
            bottom = counts_percent[cert] if bottom is None else bottom + counts_percent[cert]

    ax1.set_xlim(0,100)
    ax1.set_xlabel("Percentage (%)", fontsize=12, fontweight="bold")
    ax1.set_ylabel("", fontsize=12, fontweight="bold")
    ax1.set_title("Distribution of GRADE Judgments by Domain", fontsize=18, fontweight="bold")
    
    # Update the y-axis to include Overall Certainty
    all_domains = domains
    ax1.set_yticks(range(len(all_domains)))
    ax1.set_yticklabels(all_domains, fontsize=12, fontweight="bold")
   
    for y in range(len(all_domains)):
        ax1.axhline(y-0.5, color='lightgray', linewidth=0.8, zorder=0)

    
    for label in ax1.get_xticklabels():
        label.set_fontweight("bold")
    for label in ax1.get_yticklabels():
        label.set_fontweight("bold")

    fig.subplots_adjust(left=0.05, right=0.78, top=0.95, bottom=0.05, hspace=0.4)

    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ GRADE plot saved to {output_file}")

def plot_grade(input_file: str, output_file: str, theme="default"):
    """Generate and save a GRADE traffic-light plot from input data.
    
    This is the main public function for the grade_plot module.
    
    Args:
        input_file: Path to input file (CSV or Excel)
        output_file: Path to save the output plot
        theme: Color theme to use for the plot (default: "default")
        
    Raises:
        ValueError: If input file format is not supported or theme is invalid
    """
    df = _read_input_file(input_file)
    df = _process_grade(df)
    _grade_plot(df, output_file, theme)