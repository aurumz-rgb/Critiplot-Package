from critiplot.grade import plot_grade

def test_plot_grade():
    input_file = "sample_grade.csv"  
    output_file = "output_grade.png"
    plot_grade(input_file, output_file, theme="blue")

test_plot_grade()