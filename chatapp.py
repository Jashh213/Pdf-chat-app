import streamlit as st
st.set_page_config(page_title="Jasmitha's Smart PDF Assistant", page_icon="🧠")

# 🌐 Imports
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials/google_service_key.json"

from dotenv import load_dotenv
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError

from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.vectorstores import FAISS

# 📤 PDF Text Extraction
def extract_text_from_pdfs(pdf_files):
    text = ""
    for pdf in pdf_files:
        try:
            reader = PdfReader(pdf)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        except PdfReadError:
            st.warning(f"⚠ Skipping '{pdf.name}' — PDF could not be read.")
    return text

# ✂️ Text Chunking
def slice_text_into_chunks(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_text(text)

# 🔍 Embeddings + Vector Index
def build_vector_index(chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

# 🚀 Main App Logic
def main():
    st.title("📚 Chat With Your PDFs — Powered by Jasmitha")
    uploaded_pdfs = st.file_uploader("Choose one or more PDFs", accept_multiple_files=True, type=["pdf"])

    # Sidebar settings
    with st.sidebar:
        st.image("img/robot-image.webp", use_container_width=True)
        st.title("PDF Chatbot Settings")
        if st.button("🛠 Process PDFs"):
            if uploaded_pdfs:
                with st.spinner("🔄 Processing your documents..."):
                    raw_text = extract_text_from_pdfs(uploaded_pdfs)
                    if not raw_text.strip():
                        st.error("❌ No valid text found in PDFs.")
                        return
                    chunks = slice_text_into_chunks(raw_text)
                    build_vector_index(chunks)
                    st.success("✅ PDFs indexed successfully! Ask your question now.")
            else:
                st.error("❗ Please upload at least one PDF before processing.")

    # Chatbot Memory Setup
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    st.write("### 💬 Ask a question based on your uploaded PDFs")
    user_question = st.text_input("You:", placeholder="Ask me anything from your PDFs...")

    if user_question:
        try:
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
            llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash-latest", temperature=0.3)

            memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=vector_store.as_retriever(),
                memory=memory,
                return_source_documents=False
            )

            result = qa_chain({"question": user_question})
            response = result["answer"]

            st.session_state.chat_history.append(("You", user_question))
            st.session_state.chat_history.append(("Bot", response))

            st.markdown("### 🤖 Answer")
            st.write(response)

            st.download_button(
                label="📥 Download Answer",
                data=response,
                file_name=f"answer_to_{user_question[:15].replace(' ', '_')}.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"❌ Oops! Something went wrong: {str(e)}")

    # Chat log display
    if st.session_state.chat_history:
        with st.expander("🗂️ Chat History"):
            for sender, msg in st.session_state.chat_history[::-1]:
                st.markdown(f"**{sender}**: {msg}")

# 🎬 Run the App
if __name__ == "__main__":
    main()