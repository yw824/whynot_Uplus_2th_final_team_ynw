import streamlit as st

# from utils.db_utils import save_to_mongo
# Add the project root directory to sys.path
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pages.model_query import find_similar_doc_from_db
from scripts import pinecone_db

# Streamlit app layout
st.title("상담사용 챗봇")
st.markdown("고객의 질문에 대한 답변을 빠르게 검색하세요!")

def chatbot_query(query):
    answer = find_similar_doc_from_db(query)
    return answer.replace('  ', ' ')

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

    # response = f"**Question:** {query}\n\n**Answer:** {chatbot_invoke(query)}\n\n"
    response = f"**Question:** {query}\n\n**Answer:** {chatbot_query(query)}\n\n"

    # Add the highest similarity answer to chat history
    st.session_state["messages"].append({"role": "assistant", "content": response})

    # Display assistant response in the chat
    st.chat_message("assistant").markdown(response)

    # MongoDB 저장
    # save_to_mongo(user_input, response)

    # TODO : 유사한 질문들 답변 아래에 토글 형식으로 추가 제공 
    
    # # Display the other 3 answers (2nd to 4th) as collapsible questions
    # st.markdown("### 유사한 질문들:")
    # for i in range(1, len(retrieved_docs)):
    #     doc = retrieved_docs[i]
    #     question_part = doc.page_content.split("Question:")[-1].split("Answer:")[0].strip()
    #     answer_part = doc.page_content.split("Answer:")[-1].split("keywords:")[0].strip()
    #
    #     with st.expander(f"질문 {i+1}: {question_part}"):
    #         st.markdown(f"**Answer:** {answer_part}")
