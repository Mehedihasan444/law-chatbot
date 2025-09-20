# Bangladesh Constitution Chatbot

A law-based chatbot for Bangladesh using RAG (Retrieval-Augmented Generation) with the Constitution of the People's Republic of Bangladesh as the primary dataset.

## Features

- **High Accuracy**: Uses RAG with fine-tuned legal-specialized LLM
- **Bilingual Support**: English and Bangla language support
- **Constitutional Focus**: Limited to Constitution-based queries for maximum accuracy
- **Citation Support**: Provides article references and disclaimers
- **Hybrid Search**: Combines semantic and keyword search for better retrieval

## Project Structure

```
law chatbot/
├── src/                    # Source code
│   ├── data_processor.py   # Data extraction and preprocessing
│   ├── rag_pipeline.py     # Core RAG implementation
│   ├── chatbot.py          # Main chatbot logic
│   └── streamlit_app.py    # Web interface
├── data/                   # Dataset storage
│   ├── raw/               # Original Constitution files
│   └── processed/         # Processed and chunked data
├── config/                # Configuration files
├── tests/                 # Test files
├── vectorstore/           # Vector database storage
└── requirements.txt       # Python dependencies
```

## Installation

1. Clone the repository and navigate to the project directory
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_key_here
   PINECONE_API_KEY=your_pinecone_key_here
   ```

## Usage

1. Download the Constitution dataset:
   ```bash
   python src/data_processor.py --download
   ```
2. Process and create embeddings:
   ```bash
   python src/data_processor.py --process
   ```
3. Run the chatbot interface:
   ```bash
   streamlit run src/streamlit_app.py
   ```

## Data Sources

- Official Bangladesh Constitution (English): [WIPO](https://wipolex-res.wipo.int/edocs/lexdocs/laws/en/bd/bd025en.pdf)
- Official Bangladesh Constitution (Bangla): [WIPO](https://wipolex-res.wipo.int/edocs/lexdocs/laws/bn/bd/bd025bn.pdf)
- Ministry of Law: http://bdlaws.minlaw.gov.bd/act-details-367.html

## Accuracy Notes

- Based on Constitution of Bangladesh (1972) with 17th Amendment (2018)
- Designed for 95%+ accuracy on constitutional queries
- Includes proper citations and legal disclaimers
- Not legal advice - consult qualified lawyers for legal matters

## Testing

Run tests with:
```bash
pytest tests/
```

## Contributing

1. Ensure accuracy by testing against known constitutional provisions
2. Maintain bilingual support for all new features
3. Include proper error handling and user disclaimers
4. Follow legal and ethical guidelines for AI systems

## Legal Compliance

This chatbot complies with Bangladesh's ICT Act 2006 and includes appropriate disclaimers about not providing legal advice.