import streamlit as st
from dotenv import load_dotenv
import os
from langchain_upstage import UpstageEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from utils.db_utils import save_to_mongo
from scripts import pinecone_db

# Load environment variables
load_dotenv()
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

print(PINECONE_API_KEY)

# Embedding and Pinecone initialization
embedding = UpstageEmbeddings(model="solar-embedding-1-large", api_key=UPSTAGE_API_KEY)
index_name = 'upstage-index'
database = PineconeVectorStore.from_existing_index(index_name=index_name, embedding=embedding)

# Streamlit app layout
st.title("상담사용 챗봇")
st.markdown("고객의 질문에 대한 답변을 빠르게 검색하세요!")

def chatbot_invoke(request_str):
    retriever = database.as_retriever(
        search_type="mmr", search_kwargs={"k": 3, "fetch_k": 5}
    )

    template = """
    [context]: {context}
    ---
    [질의]: {query}
    
    7년 이상의 경력을 가진 상담사라고 생각하고, 위의 [context] 정보 내에서 [질의]에 대해 상담사 입장에서 사용자가 만족할 수 있을 정도로 성의있게 답해주세요.
    최대한 문장을 쉼표로 끊어서 대답하기 보다는 온점으로 문장을 끊어주세요. 
    문장의 마무리는 '~요' 보다는 '~다'로 끝나는 쪽이 전문적으로 보입니다.
    
    또한, 상담사는 가능한 선에서 직접 확인+안내+해결을 도와주는 직원이므로 직접 확인 후 해결까지 돕는 방향으로 작성해 주세요.
    그리고, 사용자의 편의를 위해 서비스 특성 상 쿠션어를 사용하시면 좋습니다.
    쿠션어의 예시는 다음과 같습니다.
    예시)
    불편을 드려 죄송합니다.
    번거로우시겠지만~
    ~하는 점 양해 부탁드립니다.
    ~할 예정입니다.
    ~를 부탁드립니다.
    
    위 사항들을 종합해서 2~3줄로 상담사가 활용하기 좋게 대본을 만들어 주세요.
    
    만약, 조건별로 안내 내용이 다른 경우
    1차 응대 (양해멘트 or 1차 안내 등) + 정보 확인 멘트로 대본을 구성하면 됩니다.
    정보 확인 멘트는 "정확한 상담을 위해 주문하신 주문 번호 확인 부탁드립니다." 입니다.
    문서의 아래에 각 조건별 대응 방법을 기술해 주세요.
    
    단, 제일 중요한 것은 [context] 정보에 없는 내용을 답해서는 안됩니다. [context]에 정보가 없거나 문서들의 유사성이 0.2 이하로 떨어질 경우, 
    "문의주신 내용은 확인이 필요하여 지금 답변드리기 어려울 것 같습니다. 번거로우시겠지만 확인 후에 다시 연락드려도 괜찮을까요?" 라고 답해주세요.
    """
    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

    def merge_pages(pages):
        merged = "\n".join(page.page_content for page in pages)
        return merged

    chain = (
            {"query": RunnablePassthrough(), "context": retriever | merge_pages}
            | prompt
            | llm
            | StrOutputParser()
    )

    answer = chain.invoke(request_str).replace('  ', ' ').split('.')
    return ".\n".join(answer)


# Create a session state to hold chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"}]

# Display chat history
for message in st.session_state["messages"]:
    if message["role"] == "assistant":
        st.chat_message("assistant").write(message["content"])
    else:
        st.chat_message("user").write(message["content"])

# Chat input box at the bottom
if user_input := st.chat_input("질문을 입력하세요..."):
    # Add user message to chat history
    st.session_state["messages"].append({"role": "user", "content": user_input})

    # Display the user's question in the chat
    st.chat_message("user").write(user_input)

    # Process the user's input (e.g., search for the query)
    query = user_input

    response = f"**Question:** {query}\n\n**Answer:** {chatbot_invoke(query)}\n\n"

    # Add the highest similarity answer to chat history
    st.session_state["messages"].append({"role": "assistant", "content": response})

    # Display assistant response in the chat
    st.chat_message("assistant").markdown(response)

    # MongoDB 저장
    save_to_mongo(user_input, response)

    # # Display the other 3 answers (2nd to 4th) as collapsible questions
    # st.markdown("### 유사한 질문들:")
    # for i in range(1, len(retrieved_docs)):
    #     doc = retrieved_docs[i]
    #     question_part = doc.page_content.split("Question:")[-1].split("Answer:")[0].strip()
    #     answer_part = doc.page_content.split("Answer:")[-1].split("keywords:")[0].strip()
    #
    #     with st.expander(f"질문 {i+1}: {question_part}"):
    #         st.markdown(f"**Answer:** {answer_part}")
