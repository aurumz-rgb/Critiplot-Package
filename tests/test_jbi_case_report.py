from critiplot.jbi_case_report import plot_jbi_case_report

def test_plot_jbi_case_report():
    input_file = "sample_jbi_case_report.csv" 
    output_file = "output_jbi_case_report.png"
    plot_jbi_case_report(input_file, output_file, theme="smiley_blue")

test_plot_jbi_case_report()