import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os
import numpy as np
from matplotlib.lines import Line2D
from collections import defaultdict

def process_mmat(df: pd.DataFrame) -> pd.DataFrame:
    """Process MMAT data for visualization with memory optimizations"""
    
    non_criteria_columns = {"Author_Year", "Study_Category", "Overall_Rating"}
    criteria_columns = [col for col in df.columns if col not in non_criteria_columns]
    
    required_columns = non_criteria_columns.union(criteria_columns)
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    valid_categories = {"Qualitative", "Randomized", "Non-randomized", "Descriptive", "Mixed Methods"}
    invalid_categories = set(df["Study_Category"].unique()) - valid_categories
    if invalid_categories:
        raise ValueError(f"Invalid study categories: {invalid_categories}")
    
    valid_ratings = {"Yes", "No", "Can't tell"}
    for col in criteria_columns:
        invalid_ratings = set(df[col].unique()) - valid_ratings
        if invalid_ratings:
            raise ValueError(f"Invalid ratings for {col}: {invalid_ratings}")
    
    valid_overall_ratings = {"Yes", "No", "Can't tell", "High", "Moderate", "Low"}
    invalid_overall = set(df["Overall_Rating"].unique()) - valid_overall_ratings
    if invalid_overall:
        raise ValueError(f"Invalid ratings for Overall_Rating: {invalid_overall}")
    
    df["Study_Display"] = df["Author_Year"]
    
    return df

def get_criteria_columns(df: pd.DataFrame) -> list:
    """Get criteria columns from the dataframe"""
    non_criteria_columns = {"Author_Year", "Study_Category", "Overall_Rating", "Study_Display"}
    return [col for col in df.columns if col not in non_criteria_columns]

def rating_to_risk(rating):
    """Convert MMAT rating to risk level"""
    if rating in {"Yes", "Low"}:
        return "Low"
    elif rating in {"No", "High"}:
        return "High"
    return "Moderate"

def mmat_plot(df: pd.DataFrame, output_file: str, theme: str = "default"):
    """Create MMAT visualization with memory optimizations"""
    
    criteria_columns = get_criteria_columns(df)
    
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
    
    categories = sorted(df["Study_Category"].unique())
    
    for category in categories:
        category_mask = df["Study_Category"] == category
        category_df = df[category_mask].copy()
        n_studies = len(category_df)
        n_criteria = len(criteria_columns)
        
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
        
        ax0 = fig.add_axes([0.005, ax0_bottom, 0.92, ax0_height])
        ax1 = fig.add_axes([0.05, ax1_bottom, 0.70, ax1_height])
        
        study_order = category_df["Study_Display"].tolist()
        author_pos = {a: i for i, a in enumerate(study_order)}
        all_criteria = criteria_columns + ["Overall Rating"]
        criterion_pos = {c: i for i, c in enumerate(all_criteria)}
        
        for y in range(len(author_pos)):
            ax0.axhline(y, color='lightgray', linewidth=0.8, zorder=0)
        ax0.axhline(-0.5, color='lightgray', linewidth=0.8, zorder=0)
        ax0.axhline(len(author_pos)-0.5, color='lightgray', linewidth=0.8, zorder=0)
        
        if theme.startswith("smiley"):
            symbol_map = {"Yes": "☺", "No": "☹", "Can't tell": "😐", 
                         "Low": "☺", "High": "☹", "Moderate": "😐"}
            
            for _, row in category_df.iterrows():
                y_pos = author_pos[row["Study_Display"]]
                
                for criterion in criteria_columns:
                    rating = row[criterion]
                    symbol = symbol_map.get(rating, "😐")
                    risk = rating_to_risk(rating)
                    x_pos = criterion_pos[criterion]
                    ax0.text(x_pos, y_pos, symbol, fontsize=30, ha='center', va='center', 
                            color=colors[risk], fontweight='bold', zorder=1)
                
                overall_rating = row["Overall_Rating"]
                symbol = symbol_map.get(overall_rating, "😐")
                risk = rating_to_risk(overall_rating)
                x_pos = criterion_pos["Overall Rating"]
                ax0.text(x_pos, y_pos, symbol, fontsize=30, ha='center', va='center', 
                        color=colors[risk], fontweight='bold', zorder=1)
        else:
            x_coords = []
            y_coords = []
            point_colors = []
            
            for _, row in category_df.iterrows():
                y_pos = author_pos[row["Study_Display"]]
                
                for criterion in criteria_columns:
                    rating = row[criterion]
                    risk = rating_to_risk(rating)
                    x_coords.append(criterion_pos[criterion])
                    y_coords.append(y_pos)
                    point_colors.append(colors[risk])
                
                overall_rating = row["Overall_Rating"]
                risk = rating_to_risk(overall_rating)
                x_coords.append(criterion_pos["Overall Rating"])
                y_coords.append(y_pos)
                point_colors.append(colors[risk])
            
            ax0.scatter(x_coords, y_coords, c=point_colors, s=800, marker="s", 
                       edgecolor='white', linewidth=1, zorder=1)
        
        ax0.set_xlim(-0.5, len(all_criteria)-0.5)
        ax0.set_ylim(-0.5, n_studies-0.5)
        ax0.set_xticks(range(len(all_criteria)))
        ax0.set_xticklabels(all_criteria, fontsize=11, fontweight="bold")
        ax0.set_yticks(list(author_pos.values()))
        ax0.set_yticklabels(list(author_pos.keys()), fontsize=12, fontweight="bold", rotation=0)
        ax0.set_facecolor('white')
        ax0.set_title(f"MMAT Traffic-Light Plot - {category}", fontsize=18, fontweight="bold")
        ax0.set_xlabel("")
        ax0.set_ylabel("")
        ax0.grid(axis='x', linestyle='--', alpha=0.25)
        
        bar_data = defaultdict(lambda: defaultdict(float))
        
        for criterion in criteria_columns:
            rating_counts = category_df[criterion].value_counts(normalize=True)
            for rating in ["Yes", "No", "Can't tell"]:
                percentage = rating_counts.get(rating, 0) * 100
                bar_data[criterion][rating_to_risk(rating)] += percentage
        
        overall_counts = category_df["Overall_Rating"].value_counts(normalize=True)
        for rating in ["High", "Moderate", "Low"]:
            percentage = overall_counts.get(rating, 0) * 100
            bar_data["Overall Rating"][rating_to_risk(rating)] += percentage
        
        inverted_criteria = all_criteria[::-1]
        bar_height = 0.90
        
        bottom = None
        for risk in ["High", "Moderate", "Low"]:
            values = [bar_data[criterion].get(risk, 0) for criterion in inverted_criteria]
            ax1.barh(
                inverted_criteria, 
                values, 
                left=bottom, 
                color=colors[risk], 
                edgecolor='black', 
                label=risk, 
                height=bar_height
            )
            if bottom is None:
                bottom = np.array(values)
            else:
                bottom = bottom + np.array(values)
        
        for i, criterion in enumerate(inverted_criteria):
            left = 0
            for risk in ["High", "Moderate", "Low"]:
                width = bar_data[criterion].get(risk, 0)
                if width > 0:
                    ax1.text(left + width/2, i, f"{width:.0f}%", 
                            ha='center', va='center', color='black', 
                            fontsize=12, fontweight='bold')
                    left += width
        
        ax1.set_xlim(0, 100)
        ax1.set_xticks([0, 20, 40, 60, 80, 100])
        ax1.set_xticklabels([0, 20, 40, 60, 80, 100], fontsize=12, fontweight='bold')
        ax1.set_yticks(range(len(inverted_criteria)))
        ax1.set_yticklabels(inverted_criteria, fontsize=12, fontweight='bold')
        ax1.set_xlabel("Percentage of Studies (%)", fontsize=14, fontweight="bold")
        ax1.set_ylabel("")
        ax1.set_title(f"Distribution of Ratings by Criterion - {category}", fontsize=18, fontweight="bold")
        ax1.grid(axis='x', linestyle='--', alpha=0.25)
        
        for y in range(len(inverted_criteria)):
            ax1.axhline(y-0.5, color='lightgray', linewidth=0.8, zorder=0)
        
        legend_elements = [
            Line2D([0], [0], marker='s', color='w', label='Yes/Low Risk', 
                  markerfacecolor=colors["Low"], markersize=10),
            Line2D([0], [0], marker='s', color='w', label='Cannot tell/Moderate Risk', 
                  markerfacecolor=colors["Moderate"], markersize=10),
            Line2D([0], [0], marker='s', color='w', label='No/High Risk', 
                  markerfacecolor=colors["High"], markersize=10)
        ]
        legend = ax1.legend(
            handles=legend_elements,
            title="Criterion Risk",
            bbox_to_anchor=(1.02, 1),
            loc='upper left',
            fontsize=12,
            title_fontsize=14,
            frameon=True,
            fancybox=True,
            edgecolor='black'
        )
        plt.setp(legend.get_title(), fontweight='bold')
        for text in legend.get_texts():
            text.set_fontweight('bold')
        
        category_output_file = output_file.replace(f".{output_file.split('.')[-1]}", f"_{category}.{output_file.split('.')[-1]}")
        plt.savefig(category_output_file, dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"✅ {category} plot saved to {category_output_file}")
        
        del category_df
        del bar_data

def read_input_file(file_path: str) -> pd.DataFrame:
    """Read input file (CSV or Excel) with memory optimizations"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(file_path, engine='c')
    elif ext in [".xls", ".xlsx"]:
        return pd.read_excel(file_path, engine='openpyxl')
    else:
        raise ValueError(f"Unsupported file format: {ext}. Provide a CSV or Excel file.")

def plot_mmat(input_file: str, output_file: str, theme: str = "default"):
    """
    Generate MMAT traffic-light plots from input data.
    
    Parameters:
    -----------
    input_file : str
        Path to the input CSV or Excel file containing MMAT data
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
    df = process_mmat(df)
    mmat_plot(df, output_file, theme)
    
  
    del df

if __name__ == "__main__":
    if len(sys.argv) not in [3,4]:
        print("Usage: python3 mmat_plot.py input_file output_file.(png|pdf|svg|eps) [theme]")
        sys.exit(1)

    input_file, output_file = sys.argv[1], sys.argv[2]
    theme = sys.argv[3] if len(sys.argv) == 4 else "default"

    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)

    plot_mmat(input_file, output_file, theme)