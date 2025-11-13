import pandas as pd
from xhtml2pdf import pisa
from jinja2 import Environment, FileSystemLoader
import os

def generate_csv(dataframe, output_filepath):
    """
    Generates a CSV file from a pandas DataFrame.
    """
    print(f"Starting CSV generation for {os.path.basename(output_filepath)}...")
    try:
        dataframe.to_csv(output_filepath, index=False, encoding='utf-8')
        print(f"CSV file generated successfully at: {output_filepath}")
        return True
    except Exception as e:
        print(f"Error generating CSV file: {e}")
        return False

def generate_pdf(dataframe, output_filepath, title="Material Extraction Report"):
    """
    Generates a PDF file from a pandas DataFrame using xhtml2pdf.
    """
    print(f"Starting PDF generation for {os.path.basename(output_filepath)}...")
    try:
        # Prepare data for the template
        data_for_template = dataframe.to_dict(orient='records')
        
        # Set up Jinja2 environment
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('pdf_template.html')
        
        # Render the HTML template with the data
        html = template.render(data=data_for_template)
        
        # Create the PDF
        with open(output_filepath, "w+b") as pdf_file:
            pisa_status = pisa.CreatePDF(html, dest=pdf_file)
        
        if pisa_status.err:
            print(f"Error generating PDF: {pisa_status.err}")
            return False
        
        print(f"PDF file generated successfully at: {output_filepath}")
        return True
    except Exception as e:
        print(f"Error generating PDF file: {e}")
        return False

if __name__ == '__main__':
    # --- Example Usage ---
    dummy_data = {
        'Sl. No': [1, 2],
        'Material Name': ['Cement', 'Super Long Material Name That Should Wrap'],
        'Test Name/Reference Code/Standard as per the given document (with reference page number)': [
            'This is a very long string with a lot of text that needs to wrap properly. It contains multiple sentences and should not be truncated in the final PDF. Newlines should also be handled gracefully.\n1. First point.\n2. Second point.',
            'Another long entry to test wrapping.'
        ],
        'Specific Material Type/Material Definition': [
            '43 Grade OPC. This also has some\nnewlines to test.',
            'A very specific type of material.'
        ],
        'Any other relevant information': [
            'This is the longest column with the most detailed information. It needs to be able to handle multiple paragraphs of text without any issues. The layout should remain clean and readable even with a large amount of content in this cell.\n\nThis is a new paragraph.',
            'More relevant info.'
        ]
    }
    dummy_df = pd.DataFrame(dummy_data)

    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)

    csv_path = os.path.join(output_dir, "material_report_dummy.csv")
    pdf_path = os.path.join(output_dir, "material_report_dummy.pdf")

    print(f"Generating dummy CSV at: {csv_path}")
    generate_csv(dummy_df, csv_path)

    print(f"Generating dummy PDF at: {pdf_path}")
    generate_pdf(dummy_df, pdf_path)
    print(f"Dummy files generated in '{output_dir}' directory.")
