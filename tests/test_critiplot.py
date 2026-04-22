import os
import sys
import pytest
import matplotlib
import glob


matplotlib.use('Agg')


import critiplot
from critiplot import plot_nos, plot_jbi_case_report, plot_jbi_case_series, plot_grade, plot_robis, plot_mmat


DATA_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "test_outputs")


os.makedirs(OUTPUT_DIR, exist_ok=True)

def test_plot_nos():
    """Test NOS plot generation."""
    input_file = os.path.join(DATA_DIR, "sample_nos.csv")
    output_file = os.path.join(OUTPUT_DIR, "test_nos.png")
    
    if not os.path.exists(input_file):
        pytest.skip(f"{input_file} not found")
    
    plot_nos(input_file, output_file, theme="default")
    assert os.path.exists(output_file), "NOS plot was not generated"

def test_plot_robis():
    """Test ROBIS plot generation."""
    input_file = os.path.join(DATA_DIR, "sample_robis.csv")
    output_file = os.path.join(OUTPUT_DIR, "test_robis.png")
    
    if not os.path.exists(input_file):
        pytest.skip(f"{input_file} not found")
        
    plot_robis(input_file, output_file, theme="blue")
    assert os.path.exists(output_file), "ROBIS plot was not generated"

def test_plot_grade():
    """Test GRADE plot generation."""
    input_file = os.path.join(DATA_DIR, "sample_grade.csv")
    output_file = os.path.join(OUTPUT_DIR, "test_grade.png")
    
    if not os.path.exists(input_file):
        pytest.skip(f"{input_file} not found")
        
    plot_grade(input_file, output_file, theme="green")
    assert os.path.exists(output_file), "GRADE plot was not generated"

def test_plot_jbi_case_report():
    """Test JBI Case Report plot generation."""
    input_file = os.path.join(DATA_DIR, "sample_jbi_case_report.csv")
    output_file = os.path.join(OUTPUT_DIR, "test_case_report.png")
    
    if not os.path.exists(input_file):
        pytest.skip(f"{input_file} not found")
        
    plot_jbi_case_report(input_file, output_file, theme="gray")
    assert os.path.exists(output_file), "JBI Case Report plot was not generated"

def test_plot_jbi_case_series():
    """Test JBI Case Series plot generation."""
    input_file = os.path.join(DATA_DIR, "sample_jbi_case_series.csv")
    output_file = os.path.join(OUTPUT_DIR, "test_case_series.png")
    
    if not os.path.exists(input_file):
        pytest.skip(f"{input_file} not found")
        
    plot_jbi_case_series(input_file, output_file, theme="smiley")
    assert os.path.exists(output_file), "JBI Case Series plot was not generated"

def test_plot_mmat():
    """Test MMAT plot generation."""
    input_file = os.path.join(DATA_DIR, "sample_mmat.csv")
    output_file = os.path.join(OUTPUT_DIR, "test_mmat.png")
    
    if not os.path.exists(input_file):
        pytest.skip(f"{input_file} not found")
    

    plot_mmat(input_file, output_file, theme="default")
    

    pattern = output_file.replace(".png", "_*.png")
    generated_files = glob.glob(pattern)
    
    assert len(generated_files) > 0, f"No MMAT plots were generated. Expected files matching: {pattern}"