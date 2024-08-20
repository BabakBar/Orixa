import os
import sys
import langchain_core
import langsmith
import langchain_community
from pathlib import Path
from typing import Annotated, List, Dict, Any
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.documents import Document
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from anthropic import Anthropic
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load .env file
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    logger.info(f"Loaded .env file from {env_path}")
else:
    logger.warning(f".env file not found at {env_path}")

def get_env_variable(var_name: str) -> str:
    value = os.getenv(var_name)
    if value is None:
        logger.error(f"Environment variable {var_name} is not set.")
        sys.exit(1)
    return value

anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
if not anthropic_api_key:
    logger.error("ANTHROPIC_API_KEY not found in environment variables.")
    sys.exit(1)

# Set required environment variables
try:
    os.environ["ANTHROPIC_API_KEY"] = get_env_variable("ANTHROPIC_API_KEY")
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = get_env_variable("LANGCHAIN_API_KEY")
    os.environ["LANGCHAIN_PROJECT"] = get_env_variable("LANGCHAIN_PROJECT")
except SystemExit:
    logger.error("Failed to set required environment variables. Exiting.")
    sys.exit(1)
    
# Initialize Anthropic client
anthropic_client = Anthropic(api_key=anthropic_api_key)

class DocumentLoader:
    @staticmethod
    def load(file_path: str) -> List[Document]:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        return text_splitter.split_documents(documents)

class Embedder:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings()

    def embed_documents(self, documents: List[Document]) -> Chroma:
        return Chroma.from_documents(documents, self.embeddings)

class Retriever:
    def __init__(self, vectorstore: Chroma):
        self.vectorstore = vectorstore

    def retrieve(self, query: str, k: int = 3) -> List[Document]:
        return self.vectorstore.similarity_search(query, k=k)

class State(TypedDict):
    messages: Annotated[list, add_messages]
    context: List[Document]

class RAGLangGraphApp:
    def __init__(self, documents_path: str):
        self.llm = ChatAnthropic(model_name="claude-3-sonnet-20240229", anthropic_api_key=anthropic_api_key)
        self.documents = DocumentLoader.load(documents_path)
        self.vectorstore = Embedder().embed_documents(self.documents)
        self.retriever = Retriever(self.vectorstore)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        graph_builder = StateGraph(State)
        
        def retrieval(state: State) -> Dict[str, Any]:
            query = state["messages"][-1].content
            retrieved_docs = self.retriever.retrieve(query)
            logger.info(f"Retrieved {len(retrieved_docs)} documents for query: {query}")
            return {"context": retrieved_docs}

        def rag_chatbot(state: State) -> Dict[str, Any]:
            context = "\n".join([doc.page_content for doc in state["context"]])
            logger.info(f"Context length: {len(context)} characters")
            system_message = {"role": "system", "content": f"Use the following context to answer the user's question:\n\n{context}"}
            messages = [system_message] + state["messages"]
            
            try:
                response = self.llm.invoke(messages)
                logger.info(f"Generated response length: {len(response.content)} characters")
                return {"messages": response}
            except Exception as e:
                logger.error(f"Error using LangChain ChatAnthropic: {str(e)}")
                logger.info("Falling back to direct Anthropic API call")
                try:
                    direct_response = anthropic_client.messages.create(
                        model="claude-3-sonnet-20240229",
                        max_tokens=1024,
                        messages=[
                            {"role": "system", "content": system_message["content"]},
                            {"role": "user", "content": state["messages"][-1].content}
                        ]
                    )
                    logger.info(f"Generated direct response length: {len(direct_response.content[0].text)} characters")
                    return {"messages": [{"role": "assistant", "content": direct_response.content[0].text}]}
                except Exception as e:
                    logger.error(f"Error with direct Anthropic API call: {str(e)}")
                    return {"messages": [{"role": "assistant", "content": "I'm sorry, but I encountered an error and couldn't generate a response."}]}

        graph_builder.add_node("retrieval", retrieval)
        graph_builder.add_node("rag_chatbot", rag_chatbot)
        
        graph_builder.add_edge(START, "retrieval")
        graph_builder.add_edge("retrieval", "rag_chatbot")
        graph_builder.add_edge("rag_chatbot", END)
        
        return graph_builder.compile()

    def run(self):
        print("Welcome to the RAG LangGraph App. Type 'quit' or 'q' to exit.")
        while True:
            try:
                user_input = input("User: ")
                if user_input.lower() in ["quit", "q"]:
                    print("Goodbye!")
                    break
                
                logger.info(f"Processing user input: {user_input}")
                
                response_received = False
                for event in self.graph.stream({"messages": [{"role": "user", "content": user_input}], "context": []}):
                    logger.debug(f"Received event: {event}")
                    if "messages" in event and event["messages"]:
                        assistant_response = event["messages"][-1].content
                        print("\nAssistant:", assistant_response)
                        logger.info(f"Assistant response: {assistant_response[:500]}...")
                        print("\n" + "-"*50 + "\n")
                        response_received = True
                
                if not response_received:
                    print("\nAssistant: I'm sorry, but I couldn't generate a response. Please try again.")
                    logger.warning("No response was generated for the user's input.")
                
            except KeyboardInterrupt:
                print("\nReceived interrupt. Shutting down gracefully...")
                break
            except Exception as e:
                logger.error(f"An error occurred: {str(e)}")
                print(f"\nAn error occurred: {str(e)}\nPlease try again.")    
    
def main():
    documents_path = "D:/Tools/Orixa/RAG/insights.pdf"
    try:
        app = RAGLangGraphApp(documents_path)
        app.run()
    except Exception as e:
        logger.error(f"An error occurred while initializing the app: {str(e)}")
        print("Failed to start the application. Please check the logs for more information.")

if __name__ == "__main__":
    main()