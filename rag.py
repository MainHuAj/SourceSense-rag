from uuid import uuid4
from dotenv import load_dotenv
from pathlib import Path
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PlaywrightURLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_huggingface.embeddings import HuggingFaceEmbeddings


load_dotenv()

CHUNK_SIZE = 1000
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTORSTORE_DIR = Path(__file__).parent / "resources/vectorstore"
COLLECTION_NAME = "real_estate"

llm = None
vector_store = None

def initializeComponenets():
    global llm , vector_store
    if llm is None:
        llm = ChatGroq(model="llama-3.3-70b-versatile",temperature=0.1,max_tokens=500)

    if vector_store is None:
        ef = HuggingFaceEmbeddings(
            model_name = EMBEDDING_MODEL,
            model_kwargs = {"device":"cpu"}
        )
        VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)  # ADD THIS

        vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=ef,
            persist_directory=str(VECTORSTORE_DIR)
        )

def process_urls(urls):

    yield "Initializing Components"
    initializeComponenets()

    yield "Resetting vector store"
    vector_store.reset_collection()

    yield "Loading data..."
    loader = PlaywrightURLLoader(
    urls=urls,
    remove_selectors=["header", "footer", "nav", "script", "style"],
)

    data =  loader.load()

    yield "Splitting text into chunks"
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n","\n","."," "],  
        chunk_size = CHUNK_SIZE
    )

    docs = text_splitter.split_documents(data)

    yield "Add Chunks to vector database"
    uuids = [str(uuid4()) for _ in range(len(docs))]
    vector_store.add_documents(docs,ids = uuids)

    yield "Done adding docs to vector database..."

def generate_answer(question):
    initializeComponenets()

    prompt = ChatPromptTemplate.from_template("""
    Answer the question based only on the context provided.
    
    Context: {context}
    Question: {question}
    """)

    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    # Run retrieval and question in parallel, keep both
    setup = RunnableParallel(
        context=retriever,
        question=RunnablePassthrough() 
    )

    chain = setup | {
        "answer": prompt | llm | StrOutputParser(),
        "context": lambda x: x["context"]
    }

    result = chain.invoke(question)

    answer = result["answer"]
    sources = set(doc.metadata.get("source", "") for doc in result["context"])

    return {"answer": answer, "sources": sources}




if __name__ == "__main__":
    urls = ["https://99bricks.in/the-rising-palm-floors-gurgaon-sector-95a"]
    process_urls(urls)
    result = generate_answer("Tell me about the properties?")
    print("Answer:", result["answer"])
    print("Sources:", result["sources"])