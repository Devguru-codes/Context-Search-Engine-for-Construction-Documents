# Context Search Engine - Full Frontend Application

This is the complete web application implementation of the Context Search Engine for Construction Documents. It provides a full-stack solution with Flask backend, web interface, and comprehensive document processing capabilities.

## 🚀 Features

- **Web Interface**: Clean, responsive Flask application
- **File Upload**: Drag-and-drop PDF and image upload
- **Real-time Processing**: Live progress updates during analysis
- **AI Integration**: Multiple AI models (Gemini primary, Gemma fallback)
- **Report Generation**: Automatic CSV and PDF report creation
- **Material Database**: Comprehensive construction material recognition

## 🛠️ Quick Start

1. **Navigate to the directory**:
   ```bash
   cd Full-frontend
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment**:
   ```bash
   # Download SpaCy model
   python -m spacy download en_core_web_sm

   # Create .env file with your API keys
   # GEMINI_API_KEY_1=your_key_here
   # GEMINI_API_KEY_2=your_key_here
   # GEMINI_API_KEY_3=your_key_here
   # OPENROUTER_API_KEY=your_key_here
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Open browser**: http://localhost:5000

## 📁 File Structure

```
Full-frontend/
├── app.py                 # Main Flask application
├── ai_buddy.py           # AI model integration
├── document_processor.py # PDF/Image text extraction
├── material_extractor.py # NLP material identification
├── output_generator.py   # CSV/PDF report generation
├── search_engine.py      # FAISS semantic search
├── create_index.py       # Index creation utilities
├── evaluation.py         # Model evaluation scripts
├── requirements.txt      # Python dependencies
├── templates/
│   ├── index.html       # Main upload page
│   └── pdf_template.html # PDF report template
├── uploads/             # Temporary file storage
├── downloads/           # Generated reports
├── faiss_index.idx      # Pre-built search index
├── index_to_chunk.pkl   # Index mappings
└── .gitignore          # Git ignore rules
```

## 🔧 API Configuration

The application uses multiple AI services for robustness:

- **Primary**: Google Gemini 2.0 Flash (with key rotation)
- **Fallback**: OpenRouter Gemma model
- **Keys**: Stored in `.env` file (never committed to git)

## 📊 Processing Pipeline

1. **Upload**: File validation and storage
2. **Extraction**: Text extraction from PDF/image
3. **Search**: Hybrid keyword + semantic search
4. **Analysis**: SpaCy NLP for material properties
5. **Refinement**: AI enhancement of extracted data
6. **Output**: Web display + downloadable reports

## 🛡️ Security Features

- API keys stored in environment variables
- File upload validation and cleanup
- Secure temporary file handling
- No sensitive data in source code

## 🔍 Supported Materials

The system recognizes 50+ construction materials including:
- Cement, Concrete, Steel, Aggregate
- Waterproofing, Admixtures, Reinforcement
- Timber, Glass, Insulation materials
- And many more construction-specific materials

## 📈 Performance

- **Processing Speed**: ~30 seconds for typical documents
- **Accuracy**: 85%+ material identification
- **Scalability**: Handles documents up to 100MB
- **Memory Efficient**: Optimized FAISS indexing

## 🐛 Troubleshooting

**Common Issues**:

1. **Tesseract not found**: Install Tesseract OCR
2. **API key errors**: Check `.env` file configuration
3. **Memory errors**: Reduce batch size in `ai_buddy.py`
4. **Model download**: Run `python -m spacy download en_core_web_sm`

## 🤝 Development

To contribute or modify:

1. Create feature branch
2. Make changes
3. Test with sample documents
4. Submit pull request

## 📞 Support

For technical issues, check the logs in the Flask console output or create a GitHub issue.

---

**Part of the NLP Hackathon Context Search Engine Project**
