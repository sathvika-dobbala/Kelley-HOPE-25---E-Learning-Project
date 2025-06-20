import posthog

posthog.disabled = True

from pdfprocess import PDFProcessor
from embedding import EmbeddingHandler
from langchain_ollama import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
import logging

def serve_rag():
    """Initialize the RAG system with Ollama and ChromaDB."""
    logger = logging.getLogger(__name__)
    
    # Initialize Embedding Model
    logger.info('Initializing Embedding Model. . .')
    embedding_model = OllamaEmbeddings(model = 'nomic-embed-text')
    
    # Connect to ChromaDB
    logger.info('Connecting to ChromaDB. . .')
    vectorstore = Chroma(
        embedding_function = embedding_model,
        persist_directory = './chroma_db',
        collection_name = 'harry_potter',
    )
    
    logger.warning(f'Number of documents in database: {vectorstore._collection.count()}')
    
    # Initialize LLM with Ollama
    logger.info('Initializing model -- Qwen3:8b. . .')
    llm = Ollama(model = 'qwen3:8b') # Specify specific model here
    
    # Create RetrievalQA Chain
    logger.info('Creating RetrievalQA chain. . .')
    qa_chain = RetrievalQA.from_chain_type(
        llm = llm,
        chain_type = 'stuff',
        retriever = vectorstore.as_retriever(),
        return_source_documents = True
    )
    
    return qa_chain

def rag_pdf(title):
    
    logger = logging.getLogger(__name__)
    
    # Initialize PDF Processor
    logger.info('Initializing PDF Processor. . .')
    pdf_processor = PDFProcessor(
        file_name = title,
        chunk_size = 1000,
        chunk_overlap = 100,
    )
    
    # Chunk PDF
    chunks = pdf_processor.process()
    
    # Set embedding model
    embedding_model = OllamaEmbeddings(model = 'nomic-embed-text')
    
    # Initialize ChromaDB Vector Store
    logger.info('Initializing ChromaDB Vector Store. . .')
    try:
        vectorstore = Chroma(
            collection_name = 'harry_potter',
            embedding_function = embedding_model,
            persist_directory = './chroma_db',
        )
    except Exception as e:
        logger.error(f'Error initializing ChromaDB: {e}')
        return
    
    # Embedding Handler
    embedding_handler = EmbeddingHandler(
        embedded_model = 'nomic-embed-text',
        collection = vectorstore,
    )
    
    # Process and Store Embeddings
    logger.info('Processing and storing embeddings. . .')
    if not chunks:
        logger.warning('No chunks to process. Exiting.')
        return
    embedding_handler.embed_documents(chunks)
    
    # Persist database
    vectorstore.persist()
    
if __name__ == '__main__':
    import warnings
    warnings.filterwarnings('ignore', category=DeprecationWarning)
    logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    
    # rag_pdf('hpb1.pdf') # Uncomment to process the PDF and store embeddings
    qa_chain = serve_rag() # Initialize the RAG system
    
    response = qa_chain.invoke("Who is the main antagonist in the book?")
    print(response['result'])