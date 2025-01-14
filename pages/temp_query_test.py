from model_query import *

if __name__ == "__main__":
    print("=" * 80)
    print("temp_main")
    query = "교환된 상품이 마음에 들지 않으면 어떻게 하나요?"
    print(find_similar_doc_from_db("교환된 상품이 마음에 들지 않으면 어떻게 하나요?"))