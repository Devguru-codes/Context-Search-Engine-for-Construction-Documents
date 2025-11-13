import pdfplumber
from PIL import Image
import pytesseract
import io
import os

# Set the path to the Tesseract executable for Windows
# IMPORTANT: Users may need to change this path if Tesseract is installed elsewhere.
# Download Tesseract from: https://tesseract-ocr.github.io/tessdoc/Installation.html
if os.name == 'nt': # Check if the operating system is Windows
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def process_pdf(file_path):
    """
    Extracts text and page numbers from a PDF file.
    Returns a list of dictionaries, each with 'page_number' and 'text'.
    """
    extracted_data = []
    print(f"Processing PDF: {os.path.basename(file_path)}")
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                extracted_data.append({
                    'page_number': i + 1,
                    'text': text
                })
    print(f"Finished processing PDF: {os.path.basename(file_path)}")
    return extracted_data

def process_image(file_path):
    """
    Extracts text from an image file using OCR.
    Returns a list of dictionaries, each with 'page_number' (image name) and 'text'.
    """
    extracted_data = []
    print(f"Processing image: {os.path.basename(file_path)}")
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        if text:
            # Using the file name as a "page tag" for images
            extracted_data.append({
                'page_number': os.path.basename(file_path), # Gets the filename from path
                'text': text
            })
        print(f"Finished processing image: {os.path.basename(file_path)}")
    except Exception as e:
        print(f"Error processing image {file_path}: {e}")
    return extracted_data

def process_document(file_path):
    """
    Processes a document (PDF or image) based on its file extension.
    """
    print(f"Starting document processing for {os.path.basename(file_path)}...")
    if file_path.lower().endswith('.pdf'):
        result = process_pdf(file_path)
    elif file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        result = process_image(file_path)
    else:
        raise ValueError("Unsupported file type. Please provide a PDF or image file.")
    print(f"Document processing complete for {os.path.basename(file_path)}.")
    return result

if __name__ == '__main__':
    # Example usage (for testing)
    # To run this, you'll need sample PDF and image files
    # and potentially configure pytesseract.tesseract_cmd

    # Example PDF processing
    # pdf_data = process_document('path/to/your/document.pdf')
    # for item in pdf_data:
    #    print(f"Page {item['page_number']}:\n{item['text']}\n---")

    # Example Image processing
    # image_data = process_document('path/to/your/image.png')
    # for item in image_data:
    #    print(f"Image {item['page_number']}:\n{item['text']}\n---")
    pass
