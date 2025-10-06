import logging
import os
import shutil
import time
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
BATCH_SIZE = 50

COLLECTION_NAME = "harrypotter"
# EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
# EMBEDDING_MODEL = "ai-forever/ru-en-RoSBERTa"
PROCESSED_DIR = Path(__file__).parent / "knowledge_base" / "processed"
SECRET_DIR = Path(__file__).parent / "knowledge_base" / "secret"
INDEX_DIR = Path(__file__).parent / "index"


def get_chunks(dir: Path) -> list:
    logger.debug("Splitting documents into chunks")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    chunks = []
    with tqdm(
        total=len(os.listdir(dir)),
        desc="Splitting documents into chunks",
    ) as pbar:
        for fn in sorted(dir.iterdir()):
            path = dir / fn
            docs = splitter.split_documents(TextLoader(path, encoding="utf-8").load())
            for chunk_idx, doc in enumerate(docs):
                doc.metadata["source"] = fn.name
                doc.metadata["chunk"] = chunk_idx
            chunks.extend(docs)
            pbar.update(1)

    logger.debug("Total chunks: %s", len(chunks))
    return chunks


def get_db():
    db = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL),
        persist_directory=INDEX_DIR,
    )
    return db


def build_index(chunks):
    logger.debug("Building index")
    db = get_db()
    with tqdm(total=len(chunks), desc="Building index") as pbar:
        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i : i + BATCH_SIZE]
            db.add_documents(batch)
            pbar.update(len(batch))
    logger.debug("Index built")


def main():
    if INDEX_DIR.exists():
        logger.info("Removing existing index directory at %s", INDEX_DIR)
        shutil.rmtree(INDEX_DIR)
    os.makedirs(INDEX_DIR, exist_ok=True)
    start_time = time.perf_counter()
    chunks = get_chunks(SECRET_DIR) + get_chunks(PROCESSED_DIR)
    build_index(chunks)
    end_time = time.perf_counter()
    elapsed = end_time - start_time
    logger.debug(f"Building index completed in {elapsed:.2f} seconds")


if __name__ == "__main__":
    main()
