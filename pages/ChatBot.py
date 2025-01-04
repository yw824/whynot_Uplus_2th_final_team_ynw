import streamlit as st
from dotenv import load_dotenv
import os
from langchain_upstage import UpstageEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Load environment variables
load_dotenv()
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

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

    위의 [context] 정보 내에서 [질의]에 대해 상담사 입장에서 사용자가 만족할 수 있을 정도로 성의있게 답하세요.
    단, [context] 정보에 없는 내용을 답해서는 안됩니다. 최대한 문장을 쉼표로 끊어서 대답하기 보다는, 온점으로 문장을 끊어주세요.
    이 모든 정보를 종합해서 2~3줄의 구어체로 답해주세요.

    """
    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

    def merge_pages(pages):
        merged = "\n\n".join(page.page_content for page in pages)
        return merged

    chain = (
            {"query": RunnablePassthrough(), "context": retriever | merge_pages}
            | prompt
            | llm
            | StrOutputParser()
    )

    answer = chain.invoke(request_str).replace('  ', ' ').split('.')
    return ".\n\n".join(answer)


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
    retrieved_docs = database.similarity_search(query, k=4)  # Retrieve top 4 results

    # Prepare assistant response with the highest similarity answer
    best_doc = retrieved_docs[0]

    best_question_part = best_doc.page_content.split("Question:")[-1].split("Answer:")[0].strip()
    best_answer_part = best_doc.page_content.split("Answer:")[-1].split("keywords:")[0]

    # markdown 형식으로 수정
    best_answer_part = best_answer_part.replace('\n', '\n\n')

    response = f"**Question:** {query}\n\n**Answer:** {chatbot_invoke(query)}\n\n"

    # Add the highest similarity answer to chat history
    st.session_state["messages"].append({"role": "assistant", "content": response})

    # Display assistant response in the chat
    st.chat_message("assistant").markdown(response)

    # # Display the other 3 answers (2nd to 4th) as collapsible questions
    # st.markdown("### 유사한 질문들:")
    # for i in range(1, len(retrieved_docs)):
    #     doc = retrieved_docs[i]
    #     question_part = doc.page_content.split("Question:")[-1].split("Answer:")[0].strip()
    #     answer_part = doc.page_content.split("Answer:")[-1].split("keywords:")[0].strip()
    #
    #     with st.expander(f"질문 {i+1}: {question_part}"):
    #         st.markdown(f"**Answer:** {answer_part}")
