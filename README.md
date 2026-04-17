# SourceSense — RAG-Powered Web Assistant

A general-purpose Retrieval-Augmented Generation (RAG) application that lets you query any web page in natural language. Paste up to 3 URLs, and the app scrapes the content, embeds it into a vector store, and uses LLaMA 3.3 70B to answer your questions — with sources cited.

---

## Demo

> Paste any URL → Ask questions → Get grounded answers with sources

---

## How It Works

1. **Scrape** — Playwright loads the provided URLs and extracts clean page content
2. **Chunk** — Text is split into overlapping chunks using `RecursiveCharacterTextSplitter`
3. **Embed** — Chunks are embedded using `sentence-transformers/all-MiniLM-L6-v2` and stored in ChromaDB
4. **Retrieve** — On query, the top-3 most relevant chunks are retrieved via cosine similarity
5. **Generate** — LLaMA 3.3 70B (via Groq) generates an answer grounded strictly in the retrieved context

---

## Tech Stack

| Component | Tool |
|---|---|
| LLM | LLaMA 3.3 70B via Groq |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (HuggingFace) |
| Vector Store | ChromaDB (persistent) |
| Web Scraping | Playwright (`langchain_community.PlaywrightURLLoader`) |
| Framework | LangChain (LCEL — `RunnableParallel`, `RunnablePassthrough`) |
| UI | Streamlit |

---

## Project Structure

```
SourceSense/
├── main.py              # Streamlit UI
├── rag.py               # Core RAG logic (scraping, embedding, retrieval, generation)
├── requirements.txt     # Python dependencies
├── packages.txt         # System dependencies (Chromium for Playwright)
├── setup.sh             # Playwright browser install script
├── .env.example         # Environment variable template
└── resources/
    └── vectorstore/     # ChromaDB persistent store (auto-created at runtime)
```

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/MainHuAj/SourceSense-rag.git
cd SourceSense-rag
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Open `.env` and add your Groq API key:

```
GROQ_API_KEY=your_groq_api_key_here
```

Get a free Groq API key at [console.groq.com](https://console.groq.com)

### 5. Run the app

```bash
streamlit run main.py
```

---

## Usage

1. Paste 1–3 URLs in the sidebar
2. Click **Process URLs** — wait for scraping and embedding to complete
3. Type your question in the input box
4. Get a grounded answer with source URLs cited

---

## Configuration

Key constants in `rag.py` you can tweak:

| Variable | Default | Description |
|---|---|---|
| `CHUNK_SIZE` | 1000 | Size of each text chunk in characters |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | HuggingFace embedding model |
| `temperature` | 0.1 | LLM temperature (low = factual) |
| `k` | 3 | Number of chunks retrieved per query |

---

## Limitations

- Processes up to 3 URLs at a time
- Cannot scrape pages behind authentication/login walls
- Vector store resets on each new URL processing batch
- JavaScript-heavy SPAs may not scrape perfectly

---

## Author

**Abhinav Bhatera** — 

