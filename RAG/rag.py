import posthog

posthog.disabled = True

from pdfprocess import PDFProcessor
from embedding import EmbeddingHandler
from langchain_ollama import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
import os
import logging

def serve_rag():
    from dotenv import load_dotenv
    from pathlib import Path
    dotenv_path = Path(__file__).resolve().parents[1] / '.env'
    load_dotenv(dotenv_path)
    
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
    # logger.info(f'Initializing model -- {os.getenv('RAG_MODEL')}. . .')
    llm = Ollama(model = os.getenv('RAG_MODEL')) # Specify specific model here
    
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
    
    
import torch
import torchaudio as ta
from TTS.api import TTS

# Load TTS model on import
# DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
# chatterbox_model = ChatterboxTTS.from_pretrained(device = DEVICE)
coqui_tts = TTS("tts_models/en/ljspeech/fast_pitch", progress_bar=False)

def tts(response: str):
    import soundfile as sf
    import sounddevice as sd
    
    text = response
    
    # Removes <think> </think> from LLM output
    # Only necessary for Qwen3 and Deepseek-r1 models
    if '<think>' in text:
        text = text.split('<think>')[1].split('</think>')[0]
        
    # Generate audio
    wav = coqui_tts.tts(text)
    
    # Set audio tensors for playback with default samplerate
    # audio = result.squeeze(0).cpu().numpy()
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
    
    # rag_pdf('hpb1.pdf') # Uncomment to process the PDF and store embeddings
    qa_chain = serve_rag() # Initialize the RAG system
    
    response = qa_chain.invoke("Who is the main antagonist in the book?")
    rag_response = response['result']
    tts(rag_response)