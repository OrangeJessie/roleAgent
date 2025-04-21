from write_db import ChromaVectorStore


vector_store = ChromaVectorStore('../../config/chinese_fiction.json')

vector_store.store_texts_from_file()