from critiplot.robis import plot_robis

def test_plot_robis():
    input_file = "tests/sample_robis.csv"  
    output_file = "tests/output_robis.png"
    plot_robis(input_file, output_file, theme="blue")

