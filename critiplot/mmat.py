import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
import numpy as np

def process_mmat(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process MMAT data for visualization
    """
    non_criteria_columns = ["Author_Year", "Study_Category", "Overall_Rating"]
    criteria_columns = [col for col in df.columns if col not in non_criteria_columns]
    
    required_columns = non_criteria_columns + criteria_columns
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    valid_categories = ["Qualitative", "Randomized", "Non-randomized", "Descriptive", "Mixed Methods"]
    invalid_categories = df[~df["Study_Category"].isin(valid_categories)]["Study_Category"].unique()
    if len(invalid_categories) > 0:
        raise ValueError(f"Invalid study categories: {invalid_categories}")
    
    valid_ratings = ["Yes", "No", "Can't tell"]
    for col in criteria_columns:
        invalid_ratings = df[~df[col].isin(valid_ratings)][col].unique()
        if len(invalid_ratings) > 0:
            raise ValueError(f"Invalid ratings for {col}: {invalid_ratings}")
    
    valid_overall_ratings = ["Yes", "No", "Can't tell", "High", "Moderate", "Low"]
    invalid_overall = df[~df["Overall_Rating"].isin(valid_overall_ratings)]["Overall_Rating"].unique()
    if len(invalid_overall) > 0:
        raise ValueError(f"Invalid ratings for Overall_Rating: {invalid_overall}")
    
    df["Study_Display"] = df["Author_Year"]
    
    return df

def get_criteria_names(df: pd.DataFrame):
    """
    Return the criteria names from the dataframe
    """
    non_criteria_columns = ["Author_Year", "Study_Category", "Overall_Rating", "Study_Display"]
    return [col for col in df.columns if col not in non_criteria_columns]

def rating_to_risk(rating):
    """
    Convert MMAT rating to risk level
    """
    if rating == "Yes" or rating == "Low":
        return "Low"
    elif rating == "No" or rating == "High":
        return "High"
    else:  
        return "Moderate"

def mmat_plot(df: pd.DataFrame, output_file: str, theme: str = "default"):
    """
    Create MMAT visualization in the same style as NOS
    """
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
        category_df = df[df["Study_Category"] == category]
        criteria_names = get_criteria_names(category_df)
        
        n_studies = len(category_df)
        n_criteria = len(criteria_names)
        
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
        
        plot_data = []
        for _, row in category_df.iterrows():
            for criterion in criteria_names:
                plot_data.append({
                    "Study_Display": row["Study_Display"],
                    "Criterion": criterion,
                    "Rating": row[criterion],
                    "Risk": rating_to_risk(row[criterion])
                })
            
            plot_data.append({
                "Study_Display": row["Study_Display"],
                "Criterion": "Overall Rating",
                "Rating": row["Overall_Rating"],
                "Risk": rating_to_risk(row["Overall_Rating"])
            })
        
        plot_df = pd.DataFrame(plot_data)
        
        study_order = category_df["Study_Display"].tolist()
        author_pos = {a:i for i,a in enumerate(study_order)}
        
        all_criteria = criteria_names + ["Overall Rating"]
        criterion_pos = {c:i for i,c in enumerate(all_criteria)}
        
        for y in range(len(author_pos)):
            ax0.axhline(y, color='lightgray', linewidth=0.8, zorder=0)
        
        ax0.axhline(-0.5, color='lightgray', linewidth=0.8, zorder=0)
        ax0.axhline(len(author_pos)-0.5, color='lightgray', linewidth=0.8, zorder=0)
        
        if theme.startswith("smiley"):
            def rating_to_symbol(rating):
                if rating == "Yes" or rating == "Low":
                    return "☺"
                elif rating == "No" or rating == "High":
                    return "☹"
                else: 
                    return "😐"
            
            plot_df["Symbol"] = plot_df.apply(lambda x: rating_to_symbol(x["Rating"]), axis=1)
            
            for i, row in plot_df.iterrows():
                ax0.text(criterion_pos[row["Criterion"]], author_pos[row["Study_Display"]],
                         row["Symbol"], fontsize=30, ha='center', va='center', 
                         color=colors[row["Risk"]], fontweight='bold', zorder=1)
        else:
            plot_df["x"] = plot_df["Criterion"].map(criterion_pos)
            plot_df["y"] = plot_df["Study_Display"].map(author_pos)
            
            palette = {risk: colors[risk] for risk in plot_df["Risk"].unique()}
            
            sns.scatterplot(
                data=plot_df,
                x="x",
                y="y",
                hue="Risk",
                palette=palette,
                s=800, 
                marker="s",
                legend=False,
                ax=ax0,
                edgecolor='white',
                linewidth=1
            )
        
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
        
        bar_data = []
        for criterion in criteria_names:
            rating_counts = category_df[criterion].value_counts()
            total = rating_counts.sum()
            
            for rating in ["Yes", "No", "Can't tell"]:
                count = rating_counts.get(rating, 0)
                percentage = (count / total) * 100 if total > 0 else 0
                bar_data.append({
                    "Criterion": criterion,
                    "Risk": rating_to_risk(rating),
                    "Percentage": percentage
                })
        
        overall_counts = category_df["Overall_Rating"].value_counts()
        total_overall = overall_counts.sum()
        
        for rating in ["High", "Moderate", "Low"]: 
            count = overall_counts.get(rating, 0)
            percentage = (count / total_overall) * 100 if total_overall > 0 else 0
            bar_data.append({
                "Criterion": "Overall Rating",
                "Risk": rating_to_risk(rating),
                "Percentage": percentage
            })
        
        bar_df = pd.DataFrame(bar_data)
        
        counts = bar_df.groupby(["Criterion", "Risk"]).size().unstack(fill_value=0)
        
        for risk in ["Low", "Moderate", "High"]:
            if risk not in counts.columns:
                counts[risk] = 0
        
        counts_percent = counts.div(counts.sum(axis=1), axis=0) * 100
        
        inverted_criteria = all_criteria[::-1]
        counts_percent = counts_percent.reindex(inverted_criteria)
        
        bottom = None
        bar_height = 0.90
        for risk in ["High", "Moderate", "Low"]:
            if risk in counts_percent.columns:
                ax1.barh(counts_percent.index, counts_percent[risk], left=bottom, 
                        color=colors[risk], edgecolor='black', label=risk, height=bar_height)
                bottom = counts_percent[risk] if bottom is None else bottom + counts_percent[risk]
        
        for i, criterion in enumerate(counts_percent.index):
            left = 0
            for risk in ["High", "Moderate", "Low"]:
                if risk in counts_percent.columns:
                    width = counts_percent.loc[criterion, risk]
                    if width > 0:
                        ax1.text(left + width/2, i, f"{width:.0f}%", ha='center', va='center', 
                                color='black', fontsize=12, fontweight='bold')
                        left += width
        
        ax1.set_xlim(0,100)
        ax1.set_xticks([0,20,40,60,80,100])
        ax1.set_xticklabels([0,20,40,60,80,100], fontsize=12, fontweight='bold')
        ax1.set_yticks(range(len(inverted_criteria)))
        ax1.set_yticklabels(inverted_criteria, fontsize=12, fontweight='bold')
        
        ax1.set_xlabel("Percentage of Studies (%)", fontsize=14, fontweight="bold")
        ax1.set_ylabel("")
        ax1.set_title(f"Distribution of Ratings by Criterion - {category}", fontsize=18, fontweight="bold")
        ax1.grid(axis='x', linestyle='--', alpha=0.25)
        
        for y in range(len(inverted_criteria)):
            ax1.axhline(y-0.5, color='lightgray', linewidth=0.8, zorder=0)
        
        legend_elements = [
            Line2D([0],[0], marker='s', color='w', label='Yes/Low Risk', markerfacecolor=colors["Low"], markersize=10),
            Line2D([0],[0], marker='s', color='w', label='Cannot tell/Moderate Risk', markerfacecolor=colors["Moderate"], markersize=10),
            Line2D([0],[0], marker='s', color='w', label='No/High Risk', markerfacecolor=colors["High"], markersize=10)
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
        plt.close()
        print(f"✅ {category} plot saved to {category_output_file}")

def read_input_file(file_path: str) -> pd.DataFrame:
    """
    Read input file (CSV or Excel)
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(file_path)
    elif ext in [".xls", ".xlsx"]:
        return pd.read_excel(file_path)
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