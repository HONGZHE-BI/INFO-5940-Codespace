# Ref-Log 

## External Sources and Tools

### Tools and Libraries
| Tool / Package | Purpose / Use |
|----------------|---------------|
| Streamlit | Web application framework for the chat interface |
| LangChain | RAG pipeline implementation and document processing |
| ChromaDB  | Vector database for document storage and retrieval |
| PyPDF     | PDF text extraction and processing |

### APIs
| API | Purpose |
|----------------|---------------|
| LLM Model: openai.gpt-4o | Answer generation and reasoning |
| Embedding Model: openai.text-embedding-3-small | Document embedding generation |

## GenAI Usage

1. Architecture Design

- I used ChatGPT to help me understand the langgraph file and decide to work on a langchain model.

2. Debugging & Problem Solving

- **Model Compatibility Issue**
    - Problem: Initial embedding models (text-embedding-3-large) failed with Cornell API
    - AI Assistance: Helped create *check_models.py* utility to identify available models.

- **Multi-document Retrieval**
    - Problem: Initial implementation could only process and retrieve from the first uploaded file
    - AI Assistance: Debugged vector store updating logic and implemented proper multi-document handling
    - Solution: Added sidebar diagnostics to verify all files were properly indexed in vector store

- **Duplicate File Processing**
    - Problem: Streamlit's re-execution model caused repeated processing of the same files
    - AI Assistance: Designed and implemented a content-based hashing system using filename, size, and content preview.
    - Solution: *create_file_hash()* function prevents redundant processing while maintaining performance

3. UI Polishing

- Added "Clear All Documents" functionality for testing convenience
- Implemented expandable source document viewing
- Enhanced real-time system status monitoring in sidebar