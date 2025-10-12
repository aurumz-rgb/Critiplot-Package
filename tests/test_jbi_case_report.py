from critiplot.jbi_case_report import plot_jbi_case_report

def test_plot_jbi_case_report():
    input_file = "tests/sample_jbi_case_report.csv" 
    output_file = "tests/output_jbi_case_report.png"
    plot_jbi_case_report(input_file, output_file, theme="smiley_blue")
