import streamlit as st
import os
from openai import OpenAI
from os import environ
import tempfile
import uuid
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document

client = OpenAI(
    api_key=os.environ["API_KEY"],
    base_url="https://api.ai.it.cornell.edu",
)

# Initialize LangChain LLM
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    model="openai.gpt-4o",
    temperature=0.2,
    openai_api_key=os.environ["API_KEY"],
    openai_api_base="https://api.ai.it.cornell.edu"
)

st.title("📝 File Q&A with OpenAI")
st.markdown("Upload your documents and ask questions about their content.")

# Initialize session states: messages, vectors, files
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Upload documents and ask me anything about them!"}]

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "processed_files" not in st.session_state:
    st.session_state.processed_files = []

if "processed_file_hashes" not in st.session_state:
    st.session_state.processed_file_hashes = set()

# File upload component
uploaded_files = st.file_uploader(
    "Upload document(s)", 
    type=("txt", "pdf"), 
    accept_multiple_files=True,
    help="Supports multiple .txt or .pdf files"
)

def extract_text(uploaded_file):
    """Extract text content from uploaded file"""
    try:
        file_type = uploaded_file.type
        
        if file_type == "text/plain":
            content = uploaded_file.read().decode("utf-8")
            uploaded_file.seek(0)  # Reset file pointer
            return content
            
        elif file_type == "application/pdf":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            try:
                loader = PyPDFLoader(tmp_file_path)
                documents = loader.load()
                # Combine text from all pages
                text_content = "\n".join([doc.page_content for doc in documents])
                return text_content
            finally:
                # Clean up temporary file
                os.unlink(tmp_file_path)
                
        else:
            st.warning(f"Unsupported file type: {file_type}")
            return ""
            
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return ""

# Use filename + file size + first 100 bytes of content to create hash
def create_file_hash(uploaded_file):
    """Create unique hash for file to prevent duplicate processing"""
    import hashlib
    content_preview = uploaded_file.getvalue()[:100] if hasattr(uploaded_file, 'getvalue') else b''
    hash_input = f"{uploaded_file.name}_{uploaded_file.size}_{content_preview}"
    return hashlib.md5(hash_input.encode()).hexdigest()

def process_documents(uploaded_files):
    """Process all uploaded documents and build vector store"""
    if not uploaded_files:
        return False
        
    all_documents = []
    new_files = []
    
    for uploaded_file in uploaded_files:
        file_hash = create_file_hash(uploaded_file)
        
        # Skip already processed files
        if file_hash in st.session_state.processed_file_hashes:
            continue  
            
        with st.spinner(f"Processing {uploaded_file.name}..."):
            text_content = extract_text(uploaded_file)
            
            if not text_content:
                st.warning(f"Could not extract text from {uploaded_file.name}")
                continue
            
            new_files.append(uploaded_file.name)
            
            # Create Document object
            document = Document(
                page_content=text_content,
                metadata={
                    "source": uploaded_file.name, 
                    "type": uploaded_file.type,
                    "file_hash": file_hash
                }
            )
            all_documents.append(document)
            
            # Update hashed files list
            st.session_state.processed_file_hashes.add(file_hash)
    
    if all_documents:
        # Text chunking
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100
        )
        chunks = text_splitter.split_documents(all_documents)
        
        # Create/Update vector store
        try:
            if st.session_state.vector_store is None:
                # First time creating vector store
                st.session_state.vector_store = Chroma.from_documents(
                    documents=chunks,
                    embedding=OpenAIEmbeddings(
                        model="openai.text-embedding-3-small",
                        openai_api_key=os.environ["API_KEY"],
                        openai_api_base="https://api.ai.it.cornell.edu"
                    ),
                    collection_name=f"doc_collection_{uuid.uuid4().hex[:8]}"
                )
                st.success(f"✅ Processed {len(new_files)} new file(s) with {len(chunks)} chunks")
            else:
                # Existing vector store
                current_count = st.session_state.vector_store._collection.count()
                st.session_state.vector_store.add_documents(chunks)
                new_count = st.session_state.vector_store._collection.count()
                added_count = new_count - current_count
                st.success(f"✅ Added {len(new_files)} new file(s) with {added_count} chunks")
            
            # Update processed files list
            st.session_state.processed_files.extend(new_files)
            
            return True
            
        except Exception as e:
            st.error(f"Error creating vector store: {str(e)}")
            return False
    
    return True  # Return True even if no new files to avoid reprocessing

def clear_documents():
    """Clear all documents from the system"""
    st.session_state.vector_store = None
    st.session_state.processed_files = []
    st.session_state.processed_file_hashes = set()
    st.session_state.messages = [{"role": "assistant", "content": "Upload documents and ask me anything about them!"}]
    st.success("All documents cleared!")

def rag_query(question, k=8):
    """Execute RAG query with document retrieval and generation"""
    if st.session_state.vector_store is None:
        return "Please upload documents first.", []
    
    try:
        # Retrieve relevant document chunks
        docs = st.session_state.vector_store.similarity_search(question, k=k)
        
        if not docs:
            return "I cannot find relevant information in the provided documents.", []
        
        # Build context from retrieved documents
        context = "\n\n---\n\n".join([doc.page_content for doc in docs])
        
        # Prompt template
        template = """
        You are a helpful assistant for question-answering tasks. 
        Use the following retrieved context from documents to answer the question.
        
        Context from documents:
        {context}
        
        Question: {question}
        
        Based on the context above, provide a helpful answer.
        
        Answer:
        """
        
        prompt = PromptTemplate.from_template(template)
        formatted_prompt = prompt.format(context=context, question=question)
        
        response = llm.invoke(formatted_prompt)
        return response.content, docs
        
    except Exception as e:
        return f"Error during RAG query: {str(e)}", []

# Process file uploads without duplicate processing
if uploaded_files:
    new_files = [f for f in uploaded_files if create_file_hash(f) not in st.session_state.processed_file_hashes]
    
    if new_files:
        process_documents(new_files)
    else:
        st.info("All files have already been processed.")

# File check in the sidebar
with st.sidebar:
    st.header("🔧 System Control")
    
    # Clear button
    if st.button("🗑️ Clear All Documents"):
        clear_documents()
    
    st.divider()
    
    # System status
    if st.session_state.vector_store:
        try:
            doc_count = st.session_state.vector_store._collection.count()
            st.success(f"✅ Vector store: {doc_count} chunks")
        except:
            st.success("✅ Vector store: Loaded")
    else:
        st.info("❌ Vector store: Not created")
    
    st.write(f"📁 Unique files processed: {len(st.session_state.processed_files)}")
    st.write(f"🔢 File hashes tracked: {len(st.session_state.processed_file_hashes)}")
    
    # File list
    if st.session_state.processed_files:
        st.divider()
        st.write("**Files in system:**")
        for file in st.session_state.processed_files:
            st.write(f"• {file}")

# Display processed files
if st.session_state.processed_files:
    with st.expander("📁 Processed Documents", expanded=True):
        for file_name in st.session_state.processed_files:
            st.write(f"• {file_name}")

# Display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Input
question = st.chat_input(
    "Ask something about your documents...",
    disabled=not st.session_state.processed_files
)

if question and st.session_state.processed_files:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user").write(question)
    
    # Generate answer
    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            answer, source_docs = rag_query(question)

            st.write(answer)
            
            # Display sources (collapsible)
            if source_docs:
                with st.expander("📚 Source Documents"):
                    source_files = {}
                    for doc in source_docs:
                        source = doc.metadata.get('source', 'Unknown')
                        if source not in source_files:
                            source_files[source] = 0
                        source_files[source] += 1
                    
                    st.write("**Sources found:**")
                    for source, count in source_files.items():
                        st.write(f"• {source} ({count} chunks)")
                    
                    st.divider()
                    
                    # Display specific content
                    for i, doc in enumerate(source_docs, 1):
                        st.markdown(f"**Source {i}** ({doc.metadata.get('source', 'Unknown')}):")
                        st.text(doc.page_content[:400] + "..." if len(doc.page_content) > 400 else doc.page_content)
                        st.divider()
    
    # Add assistant message to history
    st.session_state.messages.append({"role": "assistant", "content": answer})

elif question and not st.session_state.processed_files:
    st.warning("Please upload documents first before asking questions.")