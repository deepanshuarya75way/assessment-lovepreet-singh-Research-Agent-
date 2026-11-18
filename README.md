# Research Agent v4 — AI-Powered Academic Research Assistant

An AI-assisted research application designed to streamline academic literature discovery, paper analysis, evidence retrieval, research synthesis, and report generation.



## Overview

A user submits a natural-language research question and selects a publication-year range and paper limit. The application coordinates scholarly literature discovery, metadata processing, retrieval of available paper content, analysis, synthesis, and report generation.

The goal is to reduce repetitive work in an initial literature review. The application supports research; it does not replace reading original papers, expert judgment, or formal systematic-review methods.

## Problem statement

A literature review commonly requires researchers to:
- Search multiple academic sources.
- Identify and remove duplicate records.
- Review abstracts and available full-text papers.
- Compare research methods, findings, and limitations.
- Identify themes, disagreements, and possible research gaps.
- Organize references and prepare a report.

Research Agent aims to streamline parts of this workflow using academic APIs, NLP, retrieval-augmented generation (RAG), and LLM-assisted synthesis.

## Key capabilities

Depending on provider availability, configuration, and accessible documents, the application supports or is designed around:

- Natural-language research questions.
- Publication-year and paper-count filters.
- Academic literature discovery through OpenAlex and Semantic Scholar.
- Metadata normalization and duplicate handling.
- Processing available abstracts and PDF text.
- Lexical and semantic retrieval techniques.
- LLM-assisted paper analysis and literature synthesis.
- Identification of candidate research gaps and hypotheses.
- Potential contradiction or disagreement identification.
- Citation/reference organization and verification checks.
- Research relationship visualizations.
- Structured report generation and export, where enabled.
- Progress display across research workflow stages.

**Document availability:** Not every paper has an accessible full-text PDF or complete metadata. When full text is unavailable, analysis may be limited to the abstract or other available metadata.

## Research workflow

```text
Research question and filters
            |
            v
       Query planning
            |
            v
   Academic literature search
   (OpenAlex / Semantic Scholar)
            |
            v
 Normalize and deduplicate records
            |
            v
       Rank/select papers
            |
            v
 Retrieve available paper content
       (abstracts / PDFs)
            |
            v
   Extract and prepare text
            |
            v
      Evidence retrieval
            |
            v
      Paper-level analysis
            |
            v
 Potential contradiction analysis
            |
            v
       Literature synthesis
            |
            v
 Candidate gaps and hypotheses
            |
            v
    Claim/reference checks
            |
            v
   Graphs and report generation
```

Progress indicators should reflect actual backend events. A stage should be marked complete only after its operation finishes; failures should be reported rather than shown as successful completion.

## Architecture

```text
                  User
                   |
                   v
             Web interface
                   |
                   v
             FastAPI backend
                   |
                   v
        Research workflow orchestration
                   |
       +-----------+------------+
       |                        |
       v                        v
 Literature providers      Processing services
 OpenAlex                  PDF/text extraction
 Semantic Scholar          Metadata normalization
                           Deduplication
       |                        |
       +------------+-----------+
                    |
                    v
             Retrieval layer
        lexical + semantic search
                    |
                    v
              Evidence context
                    |
                    v
                LLM layer
          analysis and synthesis
                    |
          +---------+----------+
          |         |          |
          v         v          v
       Findings   Gaps     Hypotheses
          |         |          |
          +---------+----------+
                    |
                    v
       References / graphs / reports
                    |
                    v
                User interface
```

### Key design decisions

- **Multiple scholarly sources:** can broaden discovery; returned records must be normalized and deduplicated.
- **Retrieval before generation:** retrieved research content is supplied as context to the LLM instead of asking it to write from the question alone.
- **Lexical and semantic signals:** TF-IDF can help with term overlap; sentence embeddings can help find semantically related passages.
- **Modular services:** provider access, document processing, retrieval, LLM calls, and exports should remain independently maintainable.
- **Event-based progress:** progress updates should correspond to real workflow execution.

## Technology stack

These are the technologies discussed for v4. Verify actual imports and runtime paths before describing every item as active.

| Technology | Purpose |
|---|---|
| Python | Core application and research processing |
| FastAPI | Backend API and request handling |
| LangGraph | Stateful workflow orchestration, if enabled |
| Google Gemini API | LLM-assisted analysis and synthesis |
| OpenAlex | Scholarly literature discovery and metadata |
| Semantic Scholar API | Additional scholarly discovery and metadata |
| Sentence Transformers (`all-MiniLM-L6-v2`) | Dense semantic embeddings |
| scikit-learn | TF-IDF and cosine-similarity utilities |
| ChromaDB | Vector storage and similarity retrieval, where configured |
| PyMuPDF (`fitz`) | PDF text extraction |
| NetworkX | Graph representation, where enabled |
| HTML, CSS, JavaScript | Browser interface, if using the bundled web frontend |
| Server-Sent Events (SSE) | Progress streaming, if enabled |

### Retrieval concepts

- **TF-IDF** weights terms using their frequency in a document and rarity across the document collection. It is useful for lexical matching but does not inherently understand meaning.
- **Embeddings** represent text as dense numerical vectors. Sentence-transformer models can place semantically related passages near one another.
- **Cosine similarity** compares vector directions and can rank candidate passages. A similarity score is not a probability or a guarantee of relevance.

If both lexical and dense retrieval are used, document the actual score-fusion or ranking method in the code. Do not describe the system as hybrid retrieval unless both paths execute and their results are combined.

## Getting started

### Prerequisites

- Python version supported by the project's dependencies (Python 3.10+ is a reasonable starting point; check package compatibility).
- Git.
- Internet access for scholarly API calls and model/API downloads.
- A Gemini API key if Gemini generation is enabled.
- Local storage for downloaded documents and vector indexes, if used.

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repository>.git
cd <your-repository>
```

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, invoke the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

If the repository contains `requirements.txt`:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Use the Python version supported by the pinned dependencies. If installation fails, diagnose the reported package/version conflict rather than installing unrelated packages.

### 4. Configure environment variables

If `.env.example` exists, copy it:

**Windows PowerShell:**

```powershell
Copy-Item .env.example .env
```

**macOS / Linux:**

```bash
cp .env.example .env
```

Add the variable names expected by the application. For example, if the code reads `GEMINI_API_KEY`:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Gemini API access may have a free tier subject to current eligibility, quotas, and rate limits. These conditions can change. Never commit `.env` or expose credentials in source code, screenshots, logs, or public commits. Ensure `.env` is included in `.gitignore`.

## Running the application

Run the server from the directory containing the backend application. A common FastAPI/Uvicorn command is:

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

If the entry point differs, replace `app.main:app` with the actual module and ASGI variable in your repository.

Open the local URL shown by the server. If FastAPI documentation is enabled, it is commonly available at:

```text
http://127.0.0.1:8000/docs
```

Keep the backend terminal open while using the application. Stop it with `Ctrl+C`.

**Port troubleshooting:** If port `8000` is already in use, stop the existing process or start this instance on another port and use the matching URL. Avoid running multiple server instances on the same host/port.

## Using the application

1. Open the application in your browser.
2. Enter a focused research question.
3. Select the publication-year range.
4. Select the maximum number of papers.
5. Start the research workflow.
6. Follow progress in the interface.
7. Review retrieved papers and the generated synthesis.
8. Inspect candidate gaps, hypotheses, citations, and visualizations.
9. Download the report if export is enabled.

Review original papers before relying on generated interpretations.

## Project structure

The exact folder names vary by implementation. A possible logical organization is:

```text
research-agent-v4/
├── app/
│   ├── main.py                 # Backend entry point
│   ├── config.py               # Configuration and environment loading
│   ├── agents/                 # Research workflow and state
│   ├── providers/              # Academic API integrations
│   ├── services/               # Retrieval, LLM, analysis, exports
│   └── ...
├── frontend/                   # Web UI assets, if separated
├── tests/                      # Automated tests, if included
├── .env.example                # Placeholder configuration only
├── .gitignore
├── requirements.txt
└── README.md
```

Use the actual repository tree as the source of truth. Remove or rename entries that do not exist in the uploaded version.

## Reliability and code-quality considerations

- Keep API credentials in environment variables.
- Validate inputs before starting long-running work.
- Set network timeouts and handle provider errors.
- Respect API rate limits and provider terms.
- Normalize provider responses before downstream processing.
- Deduplicate using DOI where available, with a cautious fallback for missing identifiers.
- Handle missing abstracts, inaccessible PDFs, and extraction failures explicitly.
- Keep retrieval, generation, and export responsibilities modular.
- Log errors without exposing secrets.
- Test individual services and the complete workflow.
- Tie progress updates to real workflow events.
- Preserve source metadata so claims can be traced back to papers.

## Limitations

- Search coverage depends on provider coverage and available metadata.
- Full-text access is not guaranteed; some analysis may use abstracts only.
- API quotas, rate limits, and availability are controlled by external providers.
- LLM-generated summaries, gaps, hypotheses, and contradiction flags may be incomplete or incorrect.
- A citation's presence does not prove that it supports the associated claim.
- Similarity scores are ranking signals, not measures of scientific truth.
- Candidate research gaps require independent literature review and expert validation.
- This tool does not replace formal systematic-review methods, domain-expert assessment, or reading original research.

## Future improvements

- Evaluate retrieval using a labelled benchmark: Precision@k, Recall@k, MRR, and nDCG.
- Add and evaluate a cross-encoder reranker.
- Improve claim-level citation checks and evidence-span display.
- Add robust retries, rate-limit handling, and provider-failure fallbacks.
- Add persistent research history and resumable workflows.
- Expand automated tests for API adapters, retrieval, workflow stages, and exports.
- Improve PDF/table extraction and support additional document formats.
- Collect user feedback on retrieved-paper relevance.

## Security

- Do not upload API keys, `.env` files, private research documents, or personal data to a public repository.
- Keep `.env` in `.gitignore`.
- Use placeholder values only in `.env.example`.
- Review Git history before publishing; removing a secret from the latest commit does not remove it from earlier commits.
- Respect the terms, rate limits, and access conditions of external APIs and document sources.

## Acknowledgements

- [OpenAlex](https://openalex.org/) — scholarly metadata and discovery.
- [Semantic Scholar](https://www.semanticscholar.org/) — academic research discovery.
- [Google AI Studio](https://aistudio.google.com/) — Gemini API and developer resources.
- [Sentence Transformers](https://www.sbert.net/) — sentence embedding models.
- [Chroma](https://www.trychroma.com/) — vector database tooling.
- [FastAPI](https://fastapi.tiangolo.com/) — Python API framework.
- [LangGraph](https://langchain-ai.github.io/langgraph/) — graph-based workflow orchestration.

## Author


GitHub: themanwithfear(https://github.com/themanwithfear)
