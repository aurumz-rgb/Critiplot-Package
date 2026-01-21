import pandas as pd
import matplotlib.pyplot as plt
import sys
from matplotlib.patches import Patch
import numpy as np
import re
import matplotlib
import gc

matplotlib.use('Agg')  

def process_grade(df: pd.DataFrame) -> pd.DataFrame:
    """Process GRADE data with memory optimizations"""
    

    for col in df.select_dtypes(include=['int64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='integer')
    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='float')
    

    df = df.rename(columns=lambda x: x.replace('_', ' '))
    
    column_map = {
        "Other Considerations": "Publication Bias"
    }
    df = df.rename(columns=column_map)
    

    domain_columns = ["Risk of Bias", "Inconsistency", "Indirectness", "Imprecision", "Publication Bias", "Overall Certainty"]
    for col in domain_columns:
        if col in df.columns:
            df[col] = df[col].astype(str)
           
            df[col] = df[col].apply(lambda x: re.sub(r'[\x00-\x1f\x7f-\x9f]', '', str(x)).strip())

            df[col] = df[col].replace(['', 'nan', 'NaN', 'None', 'N/A', 'NA'], "Not serious")
            

            mapping_dict = {
                "not serious": "Not serious", "notserious": "Not serious", "not_serious": "Not serious",
                "none": "Not serious", "no": "Not serious", "n/a": "Not serious", "na": "Not serious",
                "serious": "Serious", "yes": "Serious",
                "very serious": "Very serious", "veryserious": "Very serious", "very_serious": "Very serious",
                "high": "High", "moderate": "Moderate", "low": "Low",
                "very low": "Very low", "verylow": "Very low", "very_low": "Very low",
                "Not Serious": "Not serious", "Notserious": "Not serious", "Not_serious": "Not serious",
                "None": "Not serious", "No": "Not serious", "N/A": "Not serious", "NA": "Not serious",
                "Serious": "Serious", "Yes": "Serious",
                "Very Serious": "Very serious", "Veryserious": "Very serious", "Very_serious": "Very serious",
                "High": "High", "Moderate": "Moderate", "Low": "Low",
                "Very Low": "Very low", "Verylow": "Very low", "Very_low": "Very low",
                "not reported": "Not reported", "notreported": "Not reported", "not_reported": "Not reported",
                "Not Reported": "Not reported", "Notreported": "Not reported", "Not_reported": "Not reported"
            }
            
            df[col] = df[col].str.lower().map(mapping_dict).fillna(df[col])
    

    required_columns = ["Outcome","Risk of Bias","Inconsistency","Indirectness","Imprecision","Publication Bias","Overall Certainty"]
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    domain_values = {"Not serious", "Serious", "Very serious"}
    certainty_values = {"High", "Moderate", "Low", "Very low"}
    

    if "Publication Bias" in df.columns and "Overall Certainty" in df.columns:
        swap_count = 0
        for idx, row in df.iterrows():
            pub_bias = row["Publication Bias"]
            overall_cert = row["Overall Certainty"]
            
            if pub_bias in certainty_values and overall_cert in domain_values:
                df.at[idx, "Publication Bias"] = overall_cert
                df.at[idx, "Overall Certainty"] = pub_bias
                swap_count += 1
        
        if swap_count > 0:
            print(f"Swapped values in {swap_count} rows between Publication Bias and Overall Certainty columns")
    
    if "Study" not in df.columns:
        df["Study"] = "Study"
    
    df["Outcome_Display"] = df["Outcome"]
    df['Original_Order'] = range(len(df))
    return df

def map_color(certainty, colors):
    """Map certainty level to color"""
    return colors.get(certainty, "grey")

def grade_plot(df: pd.DataFrame, output_file: str, theme="default"):
    """Create GRADE plot with professional design similar to robvis"""
    theme_options = {
        "green": {  
            "High":"#276A42", "Moderate":"#58C85A", "Low":"#FFDA45", "Very low":"#DD4242",
            "Not serious":"#58C85A", "Serious":"#DD4242", "Very serious":"#691625",
            "Not reported":"#999999"  
        },
        "default": {  
            "High":"#2E7D32", "Moderate":"#F78710", "Low":"#F4C81B", "Very low":"#C62828",
            "Not serious":"#2E7D32", "Serious":"#FCB33C", "Very serious":"#C62828",
            "Not reported":"#999999"
        },
        "blue": {  
            "High":"#006699", "Moderate":"#3399CC", "Low":"#F4C81B", "Very low":"#CC3333",
            "Not serious":"#3399CC", "Serious":"#CC3333", "Very serious":"#8B0000",
            "Not reported":"#999999"  
        }
    }

    if theme not in theme_options:
        raise ValueError("Invalid theme.")
    colors = theme_options[theme]

    n_studies = len(df)
    

    base_plot_height = 2.8  
    
    if n_studies <= 5:
        height_per_study = 0.3 
    elif n_studies <= 10:
        height_per_study = 0.49  
    elif n_studies <= 20:
        height_per_study = 0.63  
    elif n_studies <= 50:
        height_per_study = 0.85  
    else:
        height_per_study = 0.9 
    
    plot_height = base_plot_height + (n_studies * height_per_study)
    
    legend_text_height = 3.0 
    
    total_figure_height = plot_height + legend_text_height
    

    max_figure_height = 100.0
    if total_figure_height > max_figure_height:
        scale_factor = max_figure_height / total_figure_height
        plot_height = plot_height * scale_factor
        total_figure_height = max_figure_height
        print(f"Scaling down figure to {max_figure_height} inches to prevent memory issues")
    

    dpi = 300
    max_pixels = 178956970  
    safe_max_pixels = max_pixels * 0.85
    estimated_pixels = 24 * total_figure_height * dpi * dpi
    
    if estimated_pixels > safe_max_pixels:
        dpi = int(np.sqrt(safe_max_pixels / (24 * total_figure_height)))
        dpi = max(dpi, 50)
        print(f"Reducing DPI to {dpi} to prevent image size error")
    
    fig = plt.figure(figsize=(16.8, total_figure_height), facecolor='white')
    
    ax_bottom = legend_text_height / total_figure_height
    ax_height = plot_height / total_figure_height
    ax = fig.add_axes([0.08, ax_bottom, 0.84, ax_height])

    domains = ["Risk of Bias","Inconsistency","Indirectness","Imprecision","Publication Bias"]
    overall_certainty = "Overall Certainty"
    outcome_order = df["Outcome_Display"].tolist()
    
    domain_pos = {d: i for i, d in enumerate(domains)}
    gap_size = 0.1
    overall_pos = len(domains) + gap_size
    outcome_pos = {o: i for i, o in enumerate(outcome_order)}
    

    y_positions = list(range(len(outcome_pos))) + [-0.5, len(outcome_pos)-0.5]
    for y in y_positions:
        ax.axhline(y, color='#cccccc', linewidth=1.0, zorder=0)
    
    ax.axvline(len(domains)-0.5, color='#999999', linewidth=1.5, linestyle='--', zorder=0)
    

    domain_symbol_map = {
        "Not serious": "+",
        "Serious": "-",
        "Very serious": "X",
        "Not reported": "?"
    }
    
    certainty_symbol_map = {
        "High": "+",
        "Moderate": "~",
        "Low": "-",
        "Very low": "x"
    }
    
  
    for _, row in df.iterrows():
        y_pos = outcome_pos[row["Outcome_Display"]]
        
        for domain in domains:
            certainty = row[domain]
            x_pos = domain_pos[domain]
            color = map_color(certainty, colors)
            
            ax.scatter(x_pos, y_pos, c=color, s=1960, marker="s", edgecolor='white', linewidth=2, zorder=1)  
            symbol = domain_symbol_map.get(certainty, "?")
            ax.text(x_pos, y_pos, symbol, color='black', fontsize=37.73, ha='center', va='center', zorder=2) 
    
 
    for _, row in df.iterrows():
        y_pos = outcome_pos[row["Outcome_Display"]]
        certainty = row[overall_certainty]
        x_pos = overall_pos
        color = map_color(certainty, colors)
        
        ax.scatter(x_pos, y_pos, c=color, s=2240, marker="o", edgecolor='white', linewidth=2, zorder=1)
        symbol = certainty_symbol_map.get(certainty, "?")
        ax.text(x_pos, y_pos, symbol, color='black', fontsize=37.73, ha='center', va='center', zorder=2)  
    

    ax.set_yticks(range(len(outcome_order)))
    ax.set_yticklabels(outcome_order, fontsize=17.17, fontweight="semibold") 
    
    all_columns = domains + ["Overall Certainty"]  
    x_ticks = list(range(len(domains))) + [overall_pos]
    
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(all_columns, fontsize=17.25, fontweight="semibold")  

    ax.get_xticklabels()[-1].set_fontweight("bold")
    ax.get_xticklabels()[-1].set_fontsize(17.7) 

    ax.set_xlim(-0.5, overall_pos + 0.5)
    ax.set_ylim(-0.5, len(outcome_order)-0.5)
    ax.set_facecolor('white')
    ax.set_title("GRADE Evidence Profile", fontsize=23.72, fontweight="bold", pad=12) 
    ax.set_xlabel("", fontsize=12.94, fontweight="semibold")  
    ax.set_ylabel("", fontsize=12.94, fontweight="semibold")  
    ax.tick_params(axis='y', labelsize=17.17)  
    
  
    domain_legend_elements = [
        Patch(facecolor=colors.get("Not serious", "grey"), edgecolor='black', label="Not serious (+)"),
        Patch(facecolor=colors.get("Serious", "grey"), edgecolor='black', label="Serious (-)"),
        Patch(facecolor=colors.get("Very serious", "grey"), edgecolor='black', label="Very serious (X)"),
        Patch(facecolor=colors.get("Not reported", "grey"), edgecolor='black', label="Not reported (?)")
    ]
    
    certainty_legend_elements = [
        Patch(facecolor=colors.get("High", "grey"), edgecolor='black', label="High (+)"),
        Patch(facecolor=colors.get("Moderate", "grey"), edgecolor='black', label="Moderate (~)"),
        Patch(facecolor=colors.get("Low", "grey"), edgecolor='black', label="Low (-)"),
        Patch(facecolor=colors.get("Very low", "grey"), edgecolor='black', label="Very low (x)")
    ]
    

    legend_bottom = 0.2
    legend_height = 1.05  
    
    legend_bottom_fig = legend_bottom / total_figure_height
    legend_height_fig = legend_height / total_figure_height
    
    legend_ax1 = fig.add_axes([0.62, legend_bottom_fig, 0.18, legend_height_fig])
    legend_ax2 = fig.add_axes([0.82, legend_bottom_fig, 0.18, legend_height_fig])
    
    domain_leg = legend_ax1.legend(handles=domain_legend_elements, title="Domain Judgments", 
                                  loc='center', frameon=True, framealpha=1, edgecolor='black', 
                                  borderpad=1, fancybox=False, handlelength=2.0, handleheight=1.5)
    legend_ax1.axis('off')

    plt.setp(domain_leg.get_texts(), fontweight="normal", fontsize=18.33)  
    plt.setp(domain_leg.get_title(), fontweight="bold", fontsize=20.48) 
    
    certainty_leg = legend_ax2.legend(handles=certainty_legend_elements, title="Overall Certainty", 
                                     loc='center', frameon=True, framealpha=1, edgecolor='black', 
                                     borderpad=1, fancybox=False, handlelength=2.0, handleheight=1.5)
    legend_ax2.axis('off')

    plt.setp(certainty_leg.get_texts(), fontweight="normal", fontsize=18.33) 
    plt.setp(certainty_leg.get_title(), fontweight="bold", fontsize=20.48)  
    

    text_ax = fig.add_axes([0.08, legend_bottom_fig, 0.52, legend_height_fig])
    text_ax.axis('off')
    
    explanatory_text = (
        "1) Risk of Bias: Study design flaws\n"
        "2) Inconsistency: Results vary across studies\n"
        "3) Indirectness: Evidence not directly applicable\n"
        "4) Imprecision: Wide or uncertain estimates\n"
        "5) Publication Bias: Missing or selective studies\n"
        "6) Overall Certainty: Confidence in true effect"
    )
    
    text_ax.text(0, 0.5, explanatory_text, fontsize=19.5, va='center', ha='left', wrap=True, fontweight="normal")  
    
    plt.savefig(output_file, dpi=dpi, bbox_inches='tight', pad_inches=0.1, facecolor='white')
    plt.close(fig)
    gc.collect()  
    print(f"✅ GRADE plot saved to {output_file}")

def read_input_file(input_file: str) -> pd.DataFrame:
    """Read input file with memory optimizations"""
    if input_file.endswith(".csv"):
        try:
            usecols = ["Outcome", "Risk of Bias", "Inconsistency", "Indirectness", 
                       "Imprecision", "Publication Bias", "Other Considerations", "Overall Certainty"]
            df = pd.read_csv(input_file, engine='c', usecols=usecols)
            print("Successfully read CSV file with default settings")
        except:
            try:
                df = pd.read_csv(input_file, engine='c', encoding='latin1')
                print("Successfully read CSV file with latin1 encoding")
            except:
                try:
                    df = pd.read_csv(input_file, engine='c', sep=';')
                    print("Successfully read CSV file with semicolon separator")
                except:
                    df = pd.read_csv(input_file, engine='python')
                    print("Successfully read CSV file with python engine")
        
        if len(df) <= 20:
            print("First 5 rows of CSV file:")
            print(df.head())
            print("\nData types:")
            print(df.dtypes)
            print("\nColumn names:")
            print(df.columns.tolist())
        
        return df
    elif input_file.endswith(".xlsx") or input_file.endswith(".xls"):
        try:
            df = pd.read_excel(input_file, engine='openpyxl')
        except:
            try:
                df = pd.read_excel(input_file, engine='xlrd')
            except Exception as e:
                raise ValueError(f"Failed to read Excel file: {str(e)}")
        
        if len(df) <= 20:
            print("First 5 rows of Excel file:")
            print(df.head())
            print("\nData types:")
            print(df.dtypes)
            print("\nColumn names:")
            print(df.columns.tolist())
        
        return df
    else:
        raise ValueError("Unsupported file format. Please use .csv or .xlsx/.xls")

def plot_grade(input_file: str, output_file: str, theme="default"):
    """Generate and save a GRADE traffic-light plot from input data.
    
    Args:
        input_file: Path to input file (CSV or Excel)
        output_file: Path to save the output plot
        theme: Color theme to use for the plot (default: "default")
    """
    df = read_input_file(input_file)
    df = process_grade(df)
    gc.collect()
    grade_plot(df, output_file, theme)
    del df
    gc.collect()

if __name__ == "__main__":
    if len(sys.argv) not in [3,4]:
        print("Usage: python3 grade_plot.py input_file output_file.(png|pdf|svg|eps) [theme]")
        sys.exit(1)
    input_file, output_file = sys.argv[1], sys.argv[2]
    theme = sys.argv[3] if len(sys.argv)==4 else "default"
    
    plot_grade(input_file, output_file, theme)