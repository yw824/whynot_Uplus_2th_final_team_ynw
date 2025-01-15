import os
from dotenv import load_dotenv

from langchain_upstage import UpstageEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

# 초기 데이터 설정
load_dotenv()

def split_document(file_path: str = "../data/final_qa_list.csv"):
    """
    '../data/final_qa_list.csv'
    document = split_document(file_path)
    """

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200,
    )

    try:
        file_loader = CSVLoader(file_path=file_path, encoding='utf-8-sig')
        file_split_list = file_loader.load_and_split(text_splitter=text_splitter)
        return file_split_list
    except Exception as e:
        print(f"Error reading CSV file: {e}")


def init_pinecone_database(document, embedding_model: str ="solar-embedding-1-large", index_name: str ='upstage-index'):
    """
    database = init_pinecone_database(document=document, embedding_model=embedding_model, index_name=index_name)
    """

    embedding = UpstageEmbeddings(model=embedding_model, api_key=os.getenv("UPSTAGE_API_KEY"))

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

    index = pc.Index(index_name)
    stats = index.describe_index_stats()
    namespace_vector_count = stats.total_vector_count
    # print(namespace_vector_count)

    if namespace_vector_count is None:
        # print(f"{index_name} isn't exist")
        database = PineconeVectorStore.from_documents(document, embedding, index_name=index_name)
        return database

    else:
        # print(f"{index_name} is exist")
        database = PineconeVectorStore.from_existing_index(index_name=index_name, embedding=embedding)
        return database