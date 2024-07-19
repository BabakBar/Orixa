import streamlit as st
import tempfile
import os
from typing import List, Dict
from langchain_openai import OpenAI
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import DirectoryLoader
from langchain.vectorstores import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Atlas setup
client = os.getenv("MONGO_URI")
dbName = "orixadb"
COLLECTION_NAME = "your_collection_name"

client = MongoClient("MONGODB_ATLAS_CLUSTER_URI")
db = client["DB_NAME"]
collection = db["COLLECTION_NAME"]

# File processing function
def process_file(file_path: str) -> List[Dict[str, str]]:
    loader = UnstructuredFileLoader(file_path)
    documents = loader.load()
    
    # Extract metadata
    metadata = {
        "filename": os.path.basename(file_path),
        "filetype": os.path.splitext(file_path)[1],
        "filesize": os.path.getsize(file_path)
    }
    
    # Add metadata to each document
    for doc in documents:
        doc.metadata.update(metadata)
    
    return documents

# Text splitting and embedding
def create_vector_store(documents: List[Dict[str, str]]) -> MongoDBAtlasVectorSearch:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    
    embeddings = OpenAIEmbeddings()
    
    vector_store = MongoDBAtlasVectorSearch.from_documents(
        texts,
        embeddings,
        collection=collection,
        index_name="default"  # Make sure this index exists in your MongoDB Atlas cluster
    )
    
    return vector_store

# Streamlit file uploader
def file_uploader():
    uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            try:
                st.write(f"Processing {uploaded_file.name}...")
                documents = process_file(tmp_file_path)
                vector_store = create_vector_store(documents)
                st.success(f"Successfully processed and stored {uploaded_file.name}")
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {str(e)}")
            finally:
                os.unlink(tmp_file_path)

# Main function
def main():
    st.title("RAG File Upload and Processing")
    file_uploader()

if __name__ == "__main__":
    main()