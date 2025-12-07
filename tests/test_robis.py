from critiplot.robis import plot_robis

def test_plot_robis():
    input_file = "sample_robis.csv"  
    output_file = "output_robis.png"
    plot_robis(input_file, output_file, theme="blue")

test_plot_robis()

