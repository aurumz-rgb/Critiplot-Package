from critiplot.jbi_case_series import plot_jbi_case_series

def test_plot_jbi_case_series():
    input_file = "sample_jbi_case_series.csv"  
    output_file = "output_jbi_case_series.png"
    plot_jbi_case_series(input_file, output_file, theme="smiley")

test_plot_jbi_case_series()