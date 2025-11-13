from flask import Flask, render_template, request, send_file
import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file at the very beginning
load_dotenv()

from document_processor import process_document
from material_extractor import extract_information
from output_generator import generate_csv, generate_pdf
from ai_buddy import refine_batch_with_ai # Import the new batch refinement function

# Initialize the Flask application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DOWNLOAD_FOLDER'] = 'downloads' # New folder for generated reports
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)


@app.route('/', methods=['GET'])
def index():
    """
    Serve the main landing page with file upload form.
    """
    return render_template('index.html', result_table=None, csv_link=None, pdf_link=None)


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handles file upload, processes the document, extracts information,
    refines it with AI, and displays it in a table. Also generates CSV and PDF reports.
    """
    if 'document' not in request.files:
        return render_template('index.html', result_table="No document part in the request", error=True)
    
    file = request.files['document']
    
    if file.filename == '':
        return render_template('index.html', result_table="No selected file", error=True)
    
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        print(f"File '{file.filename}' uploaded successfully.")
        
        try:
            print("Document processing starts...")
            # Process the document
            document_data = process_document(filepath)
            print("Document processed.")
            
            print("Material information extraction starts...")
            # Extract material information
            extracted_df = extract_information(document_data)
            print("Material information extracted.")
            
            print("AI refinement starts...")
            
            # Convert DataFrame to list of dictionaries for AI processing
            extracted_list = extracted_df.to_dict(orient='records')
            
            # Process in batches of 3 with AI refinement
            refined_list = []
            batch_size = 3 # As per user's request to send 3 rows together
            for i in range(0, len(extracted_list), batch_size):
                batch = extracted_list[i:i + batch_size]
                # The refine_batch_with_ai function now handles sending the entire batch in one prompt
                refined_batch = refine_batch_with_ai(batch)
                refined_list.extend(refined_batch)
            
            # Convert the refined list back to a DataFrame
            # Ensure the conversion handles cases where AI might return fewer items or in a different order
            refined_df = pd.DataFrame(refined_list)
            print("AI refinement complete.")

            # Filter out rows where the merged reference column is empty
            col_name = 'Test Name/Reference Code/Standard as per the given document (with reference page number)'
            
            # Use refined_df for all subsequent operations
            # Ensure 'col_name' exists in the refined_df, or handle cases where AI might modify column names
            if col_name in refined_df.columns:
                refined_df = refined_df[refined_df[col_name] != "No Information Available"]
                print("Filtered out empty reference rows.")

            # Re-assign serial numbers after filtering
            refined_df.reset_index(drop=True, inplace=True)
            refined_df['Sl. No'] = refined_df.index + 1
            print("Serial numbers re-assigned.")
            
            # Prepare for HTML display by replacing newlines with <br> tags
            df_for_html = refined_df.copy()
            if col_name in df_for_html.columns:
                df_for_html[col_name] = df_for_html[col_name].astype(str).str.replace('\n', '<br>')
            print("Prepared data for HTML display.")

            # Convert DataFrame to HTML table, preventing escaping of <br> tags
            result_html = df_for_html.to_html(index=False, classes='table', escape=False)
            print("Converted data to HTML table.")

            # Generate CSV report
            print("Generating CSV report...")
            csv_filename = "material_report.csv"
            csv_filepath = os.path.join(app.config['DOWNLOAD_FOLDER'], csv_filename)
            generate_csv(refined_df, csv_filepath)
            csv_link = f"/download/{csv_filename}"
            print(f"CSV report generated: {csv_filepath}")

            # Generate PDF report
            print("Generating PDF report...")
            pdf_filename = "material_report.pdf"
            pdf_filepath = os.path.join(app.config['DOWNLOAD_FOLDER'], pdf_filename)
            generate_pdf(refined_df, pdf_filepath)
            pdf_link = f"/download/{pdf_filename}"
            print(f"PDF report generated: {pdf_filepath}")
            
            return render_template('index.html', result_table=result_html, csv_link=csv_link, pdf_link=pdf_link)
        except Exception as e:
            print(f"An error occurred during file processing: {e}")
            return render_template('index.html', result_table=f"Error processing file: {e}", error=True)
        finally:
            # Clean up: remove the uploaded file if it exists
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"Cleaned up uploaded file: {filepath}")
    
    return render_template('index.html', result_table="An unexpected error occurred", error=True)

@app.route('/download/<filename>')
def download_file(filename):
    """
    Provides a download link for generated files.
    """
    return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'], filename), as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
