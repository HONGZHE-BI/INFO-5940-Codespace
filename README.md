# INFO 5940 Assignment 1: File Q&A with OpenAI

A Retrieval-Augmented Generation (RAG) application built with Streamlit and LangChain that allows users to upload documents and interact with their content through a conversational interface.

## Features
- **Multi-format Document Uploading**: Support both .txt and .pdf files.
- **Multi-document Handling**: Support for multiple document uploads and interaction across all documents.
- **Efficient Chunking**: Automatic text splitting with configurable chunk size and overlap.
- **Vector Store Construction**: Builds or updates ChromaDB to store embeddings of document chunks.  
- **Similarity‑based Retrieval**: Performs vector search to find the most relevant content for each query.  
- **RAG‑based Answer Generation**: Uses the OpenAI API to generate responses grounded in the retrieved context.  
- **Interactive Chat Interface**: Built with Streamlit, showing full dialogue history.  
- **Source Traceability**: Displays which document(s) and chunk(s) each answer was based on.  
- **Duplicate & State Management**: Automatically tracks processed files using MD5 hashes and allows clearing all stored data.

## RAG Pipeline

```
User Uploads Files (.pdf/.txt) 
         ↓
Text Extraction & Chunking (800 chars, 100 overlap)
         ↓
Embedding Generation (openai.text‑embedding‑3‑small)
         ↓
Vector Storage (ChromaDB)
         ↓
User Asks Question
         ↓
Semantic Search (k=8 chunks)
         ↓
Context Building & Prompt Creation
         ↓
LLM Generation (openai.gpt‑4o)
         ↓
Display Answer + Source Documents
```

## Extra Key Designs

1. **File Hashing System**: For user-friendly execution and memeory optimization.
2. **System Control Sidebar**: For real-time monitoring and user control transparency.






## How to Run

1. Install Dependencies
```bash
pip install -r requirements.txt
```

2. Set up API Key
```bash
export API_KEY="api_key"
```

3. Run the APP
```bash
streamlit run chat_with_pdf.py
```

## Dependency Modifications
1. **requirements.txt**: The library lists that the APP depends on, just adding the ChromaDB dependencies for the robustness.
   ```bash
   #Chromadb
   chromadb>=0.4.0
   langchain-chroma>=0.1.0
   ```
2. **check_models.py**: An auxiliary Python file to check which LLM model and embedding model the API Key supports. You can change the models as you want.