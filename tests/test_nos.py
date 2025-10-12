from critiplot.nos import plot_nos

def test_plot_nos():
    input_file = "tests/sample_nos.csv"      
    output_file = "tests/output_nos.png"
    plot_nos(input_file, output_file, theme="default")
