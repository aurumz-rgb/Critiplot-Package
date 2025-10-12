from critiplot.grade import plot_grade

def test_plot_grade():
    input_file = "tests/sample_grade.csv"  
    output_file = "tests/output_grade.png"
    plot_grade(input_file, output_file, theme="blue")
