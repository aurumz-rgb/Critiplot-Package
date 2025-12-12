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

    df['Original_Order'] = range(len(df))
    
    domain_columns = ["Risk of Bias","Inconsistency","Indirectness","Imprecision","Publication Bias","Overall Certainty"]
    for col in domain_columns:
        if col in df.columns:
            df[col] = df[col].fillna("None")

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
            "Very Low":"#5D6975",
            "None":"#B5B5B5"
        },
        "default": {  
            "High":"#276A42",
            "Moderate":"#61BF61",
            "Low":"#F4D043",
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

    domains = ["Risk of Bias","Inconsistency","Indirectness","Imprecision","Publication Bias", "Overall Certainty"]
    
    # Fixed parameters (this fixes the major gap issue, very important)
    n_studies = len(df)
    per_study_height = 0.5  
    min_first_plot_height = 4.0  
    second_plot_height = 3.0  
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
    
    plot_data = []
    for _, row in df.iterrows():
        for domain in domains:
            plot_data.append({
                "Outcome_Display": row["Outcome_Display"],
                "Domain": domain,
                "Certainty": row[domain],
                "Original_Order": row["Original_Order"]
            })
    
    plot_df = pd.DataFrame(plot_data)
    plot_df["Color"] = plot_df["Certainty"].apply(lambda x: _map_color(x, colors))
    
    outcome_order = df.sort_values("Original_Order")["Outcome_Display"].tolist()
    plot_df["Outcome_Display"] = pd.Categorical(
        plot_df["Outcome_Display"], 
        categories=outcome_order, 
        ordered=True
    )
    
    sns.scatterplot(
        data=plot_df, 
        x="Domain", 
        y="Outcome_Display",
        hue="Color", 
        palette={c:c for c in plot_df["Color"].unique()},
        s=800, 
        marker="s", 
        legend=False, 
        ax=ax0
    )
    
    ax0.set_yticks(range(len(outcome_order)))
    ax0.set_yticklabels(outcome_order, fontsize=10, fontweight="bold")
    
    for y in range(len(outcome_order)):
        ax0.axhline(y, color='lightgray', linewidth=0.8, zorder=0)
    ax0.axhline(-0.5, color='lightgray', linewidth=0.8, zorder=0)
    ax0.axhline(len(outcome_order)-0.5, color='lightgray', linewidth=0.8, zorder=0)

    ax0.set_xticks(range(len(domains)))
    ax0.set_xticklabels(domains, fontsize=12, fontweight="bold")
    ax0.set_xlim(-0.5, len(domains)-0.5)

    ax0.set_ylim(-0.5, len(outcome_order)-0.5)
    ax0.set_facecolor("white")

    ax0.set_title("GRADE Traffic-Light Plot", fontsize=18, fontweight="bold")
    ax0.set_xlabel("GRADE Domains", fontsize=12, fontweight="bold")
    ax0.set_ylabel("", fontsize=12, fontweight="bold")
    ax0.tick_params(axis='y', labelsize=10)

    legend_elements = [Patch(facecolor=colors[c], edgecolor='black', label=c) for c in ["High","Moderate","Low","Very Low","None"]]
    leg = ax0.legend(handles=legend_elements, title="Certainty", bbox_to_anchor=(1.02,1), loc='upper left', frameon=True, borderpad=1)
    plt.setp(leg.get_texts(), fontweight="bold")
    plt.setp(leg.get_title(), fontweight="bold")

    bar_data = []
    for domain in domains:
        certainty_counts = df[domain].value_counts()
        total = certainty_counts.sum()
        
        for certainty in ["High", "Moderate", "Low", "Very Low", "None"]:
            count = certainty_counts.get(certainty, 0)
            percentage = (count / total) * 100 if total > 0 else 0
            bar_data.append({
                "Domain": domain,
                "Certainty": certainty,
                "Count": count,
                "Percentage": percentage
            })
    
    bar_df = pd.DataFrame(bar_data)
    
    inverted_domains = domains[::-1]
    bar_df['Domain'] = pd.Categorical(bar_df['Domain'], categories=inverted_domains, ordered=True)
    
    bottom = pd.Series([0.0] * len(inverted_domains), index=inverted_domains)
    for cert in ["Very Low", "Low", "Moderate", "High", "None"]:
        cert_data = bar_df[bar_df['Certainty'] == cert]
        if not cert_data.empty:
            cert_series = pd.Series(0.0, index=inverted_domains)
            for _, row in cert_data.iterrows():
                cert_series[row['Domain']] = row['Percentage']
            
            ax1.barh(
                range(len(inverted_domains)), 
                cert_series, 
                left=bottom,
                color=colors[cert], 
                edgecolor="black", 
                linewidth=1.5, 
                label=cert
            )
            
           
            bottom_array = bottom.values
            for i, domain in enumerate(inverted_domains):
                val = cert_series[domain]
                if val > 0: 
                    ax1.text(
                        bottom_array[i] + val/2, 
                        i, 
                        f"{val:.1f}%", 
                        va='center', 
                        ha='center', 
                        fontsize=10, 
                        color='black', 
                        fontweight="bold"
                    )
            
            bottom = bottom + cert_series

    ax1.set_xlim(0,100)
    ax1.set_xlabel("Percentage (%)", fontsize=12, fontweight="bold")
    ax1.set_ylabel("", fontsize=12, fontweight="bold")
    ax1.set_title("Distribution of GRADE Judgments by Domain", fontsize=18, fontweight="bold")
    
    ax1.set_yticks(range(len(inverted_domains)))
    ax1.set_yticklabels(inverted_domains, fontsize=12, fontweight="bold")
    
    for y in range(len(inverted_domains)):
        ax1.axhline(y-0.5, color='lightgray', linewidth=0.8, zorder=0)

    for label in ax1.get_xticklabels():
        label.set_fontweight("bold")
    for label in ax1.get_yticklabels():
        label.set_fontweight("bold")

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