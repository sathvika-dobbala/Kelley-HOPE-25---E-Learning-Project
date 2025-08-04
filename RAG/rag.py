import posthog

posthog.disabled = True

from pdfprocess import PDFProcessor
from embedding import EmbeddingHandler
from langchain_ollama import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
import os
import logging

import yaml
# Loading config from config YAML
with open('RAG/config.yaml', 'r') as f:
    CONFIG = yaml.safe_load(f)
    
from dotenv import load_dotenv
from pathlib import Path
# Loading environment variables
dotenv_path = Path(__file__).resolve().parents[1] / '.env'
load_dotenv(dotenv_path)
    
def serve_rag():
    """Initialize the RAG system with Ollama and ChromaDB."""
    
    logger = logging.getLogger(__name__)
    
    embedding_model = OllamaEmbeddings(model = CONFIG['embedding_model']['name'])
    
    logger.info('Connecting to ChromaDB. . .')
    vectorstore = Chroma(
        embedding_function = embedding_model,
        persist_directory = CONFIG['chroma_db']['persist_directory'],
        collection_name = CONFIG['chroma_db']['collection_name'],
    )
    
    logger.warning(f'Number of documents in database: {vectorstore._collection.count()}')
    if vectorstore._collection.count() == 0:
        logger.error('No documents found in the vector store. Please ensure embeddings are processed and stored.')
        return
    
    # ToDo: Add switch for different LLMs
    llm = Ollama(model = CONFIG['llm']['ollama_model'])
    
    # Utilizing Gemini API
    # llm = ChatGoogleGenerativeAI(
    #     model = os.getenv('GEMINI_MODEL'),
    #     google_api_key = os.getenv('GOOGLE_API_KEY'),
    #     temperature = 0
    # )
    
    logger.info('Creating RetrievalQA chain. . .')
    qa_chain = RetrievalQA.from_chain_type(
        llm = llm,
        chain_type = CONFIG['retrieval_qa']['chain_type'],
        retriever = vectorstore.as_retriever(search_kwargs={'k': CONFIG['retrieval_qa']['retrieve_k']}),
        return_source_documents = True
    )
    
    return qa_chain

def embed_pdf(title):
    
    logger = logging.getLogger(__name__)
    
    logger.info('Initializing PDF Processor. . .')
    pdf_processor = PDFProcessor(
        file_name = title,
        chunk_size = CONFIG['pdf_processor']['chunk_size'],
        chunk_overlap = CONFIG['pdf_processor']['chunk_overlap'],
    )
    
    chunks = pdf_processor.process()
    
    embedding_model = OllamaEmbeddings(model = CONFIG['embedding_model']['name'])
    
    logger.info('Initializing ChromaDB Vector Store. . .')
    
    try:
        vectorstore = Chroma(
            embedding_function = embedding_model,
            persist_directory = CONFIG['chroma_db']['persist_directory'],
            collection_name = CONFIG['chroma_db']['collection_name'],
        )
    except Exception as e:
        logger.error(f'Error initializing ChromaDB: {e}')
        return
    
    embedding_handler = EmbeddingHandler(
        embedded_model = embedding_model,
        collection = vectorstore,
    )
    
    logger.info('Processing and storing embeddings. . .')
    if not chunks:
        logger.warning('No chunks to process. Exiting.')
        return
    
    embedding_handler.embed_documents(chunks)
    
    
from TTS.api import TTS

# Load TTS model on import
# DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
coqui_tts = TTS(CONFIG['tts']['model'], progress_bar=False)

def tts(text: str):
    import soundfile as sf
    import sounddevice as sd
    
    # Removes <think> </think> from LLM output
    # Only necessary for Thinking Models like Qwen3 and Deepseek-r1
    if '<think>' in text:
        text = text.split('</think>')[1]
        
    # Generate audio
    wav = coqui_tts.tts(text)
    
    sd.play(wav, samplerate = 22050)
    sd.wait()

async def tts_async(text: str):
    import asyncio
    ''' Run TTS in background'''
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, tts, text)
    
def run_rag(query: str):
    qa_chain = serve_rag()
    return qa_chain.invoke(query)
    
if __name__ == '__main__':
    
    import warnings
    warnings.filterwarnings('ignore', category=DeprecationWarning)
    logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # embed_pdf('redbook.pdf') # Uncomment to process the PDF and store embeddings
    qa_chain = serve_rag() # Initialize the RAG system
    
    response = qa_chain.invoke("Can you summarize chapter 5: routing protocols in detail?")
    rag_response = response['result']
    print(rag_response)