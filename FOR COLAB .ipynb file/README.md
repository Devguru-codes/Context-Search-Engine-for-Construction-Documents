# Context-Aware Search Engine for Material Specifications

This project is a web-based application designed to extract and analyze material specifications from technical documents, primarily in PDF and image formats. It uses a combination of OCR, natural language processing (NLP), and generative AI to identify relevant materials, extract their properties, and present them in a structured and user-friendly format.

## Features

-   **File Upload**: Users can upload technical documents (PDFs and images) through a web interface.
-   **Text Extraction**: The application uses `pdfplumber` for PDFs and `pytesseract` for images to extract raw text from the documents.
-   **Hybrid Material Search**: The application uses a sophisticated hybrid search model that combines traditional keyword matching with advanced semantic search. This allows for more accurate and comprehensive identification of materials, even when the terminology varies.
-   **Information Extraction**: The tool uses `spacy` and regular expressions to extract detailed information related to the identified materials, including IS codes, headings, and other contextual data, from the results of the hybrid search.
-   **AI-Powered Refinement**: The extracted information is then processed by a generative AI model (Gemini or Gemma) to refine and enrich the data, providing more accurate and comprehensive details.
-   **Structured Output**: The final results are displayed in a clean, tabular format on the web page.
-   **Report Generation**: Users can download the extracted and refined information as both CSV and PDF reports.

## How It Works

The application follows a multi-step process to analyze the documents:

1.  **Document Upload**: The user uploads a file through the Flask web interface.
2.  **Processing**: `document_processor.py` handles the uploaded file, extracting text using the appropriate library based on the file type.
3.  **Hybrid Extraction**: `material_extractor.py` processes the extracted text using a hybrid approach:
    *   **Semantic Search**: A semantic index of the document is created using `sentence-transformers` and `faiss-cpu` to find textually similar content.
    *   **Keyword Search**: A traditional keyword search is also performed to ensure all relevant sections are found.
    *   The results from both searches are combined to create a comprehensive set of contexts.
4.  **AI Refinement**: `ai_buddy.py` sends the combined and enriched data to a generative AI model. The AI is prompted to act as a civil engineering expert, refining the data to be more accurate and detailed.
5.  **Output Generation**: `output_generator.py` creates CSV and PDF reports from the refined data, which are then made available for download.

## Setup and Installation

To run this project locally, follow these steps:

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Tesseract OCR**:
    -   Download and install Tesseract from the [official repository](https://tesseract-ocr.github.io/tessdoc/Installation.html).
    -   Ensure that the Tesseract executable path is correctly configured in `document_processor.py`.

5.  **Set up API Keys**:
    -   Create a `.env` file in the root directory.
    -   Add your API keys for Gemini and OpenRouter to the `.env` file:
        ```
        GEMINI_API_KEY="your_gemini_api_key"
        OPENROUTER_API_KEY="your_openrouter_api_key"
        ```

6.  **Download SpaCy Model**:
    ```bash
    python -m spacy download en_core_web_sm
    ```

7.  **Run the application**:
    ```bash
    flask run
    ```
    The application will be available at `http://127.0.0.1:5000`.

## Dependencies

The project relies on the following major libraries:

-   **Flask**: For the web framework.
-   **pandas**: For data manipulation.
-   **pdfplumber**: For PDF text extraction.
-   **pytesseract**: For OCR.
-   **spacy**: For natural language processing.
-   **sentence-transformers**: For creating sentence embeddings.
-   **faiss-cpu**: For efficient similarity search.
-   **torch** and **transformers**: As dependencies for `sentence-transformers`.
-   **google-generativeai**: For Gemini API integration.
-   **requests**: For OpenRouter API integration.
-   **reportlab**: For PDF generation.

A complete list of dependencies can be found in `requirements.txt`.
