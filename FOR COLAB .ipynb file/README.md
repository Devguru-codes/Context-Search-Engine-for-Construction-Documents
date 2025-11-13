# Context Search Engine - Colab Notebook Version

This Jupyter notebook provides a complete implementation of the Context Search Engine for Construction Documents, optimized for Google Colab environment. It includes all the same functionality as the full web application but runs entirely in a notebook interface.

## 🚀 Features

- **Colab Optimized**: Runs directly in Google Colab
- **No Local Setup**: Everything runs in the cloud
- **Interactive**: Step-by-step execution with progress updates
- **Complete Pipeline**: From document upload to report generation
- **AI Integration**: Same AI models as the web version

## 🛠️ Quick Start in Colab

1. **Open the notebook**:
   - Go to: `FOR COLAB .ipynb file/Colab_file_final.ipynb`
   - Click "Open in Colab" or upload to Google Colab

2. **Set up secrets**:
   - Click the 🔑 (key) icon in the left sidebar
   - Add these secrets:
     ```
     GEMINI_API_KEY_1: your_gemini_key_1
     GEMINI_API_KEY_2: your_gemini_key_2
     GEMINI_API_KEY_3: your_gemini_key_3
     OPENROUTER_API_KEY: your_openrouter_key
     ```

3. **Run all cells**:
   - Click "Runtime" → "Run all"
   - Follow the prompts to upload your document

4. **Download results**:
   - CSV and PDF reports will be automatically generated
   - Download links appear at the end

## 📊 What It Does

The notebook processes construction documents to extract material specifications:

1. **Document Upload**: Upload PDF or image files
2. **Text Extraction**: OCR for images, direct parsing for PDFs
3. **Material Identification**: Advanced NLP to find construction materials
4. **Property Extraction**: Pulls specifications, standards, and requirements
5. **AI Enhancement**: Uses Gemini AI to refine and complete the data
6. **Report Generation**: Creates professional CSV and PDF reports

## 🔧 Technical Details

- **AI Models**: Gemini 2.0 Flash with Gemma fallback
- **NLP Engine**: SpaCy with custom construction material patterns
- **Search Algorithm**: Hybrid keyword + semantic search with FAISS
- **Output Formats**: Interactive tables, CSV, PDF reports

## 📋 Supported File Types

- **PDF**: Direct text extraction with pdfplumber
- **Images**: OCR processing with Tesseract
- **Formats**: PNG, JPG, JPEG, TIFF, BMP

## 🛡️ Security in Colab

- API keys stored in Colab secrets (not visible in notebook)
- Temporary files automatically cleaned up
- No sensitive data saved in the notebook

## ⚡ Performance

- **Typical Processing**: 1-3 minutes per document
- **Accuracy**: 85%+ material identification
- **Batch Processing**: Handles multiple materials efficiently

## 🐛 Common Issues

1. **"Module not found"**: Run the installation cells first
2. **API quota exceeded**: The system automatically rotates between your API keys
3. **OCR fails**: Ensure image quality is good (300+ DPI recommended)
4. **Memory issues**: Colab has 12GB RAM limit - reduce batch sizes if needed

## 📈 Advanced Usage

- **Custom Materials**: Edit the `CORE_KEYWORDS` list to add new materials
- **Batch Processing**: Modify batch sizes in the AI refinement section
- **Output Customization**: Edit the PDF template for different report formats

## 🔗 Related Files

- **Full Web App**: Check `../Full-frontend/` for the complete Flask application
- **Main README**: See `../README.md` for project overview

## 🤝 Contributing

To improve the Colab version:

1. Test changes thoroughly in Colab environment
2. Ensure compatibility with Colab's resource limits
3. Update this README with any new features

## 📞 Support

- Check Colab runtime logs for detailed error messages
- Ensure all dependencies install correctly
- Verify API keys are properly set in secrets

---

**Colab Version - Part of the NLP Hackathon Context Search Engine Project**
