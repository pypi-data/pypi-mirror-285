# VersaCore

The VersaCore Python library

## Installation

```bash
pip install versacore
```

 # Web Article Summarize Query API

This project provides an API to summarize or query articles from a given URL using the Large Language Model (LLM). The API can be used with various models and APIs, such as lmstudio.

## Usage

### Summarize an Article

To summarize an article from a URL:

```bash
python webArticleSummariseQuery.py --url "https://example.com/article" --model "your_desired_model"
```

The summarized content will be printed to the console.

### Query an Article

To query an article with a specific question:

```bash
python webArticleSummariseQuery.py --url "https://example.com/article" --model "your_desired_model" --query "What is the main point of this article?"
```

The answer to your question will be printed to the console.

### Running the API Server

To run the Flask server and access the API, use:

```bash
python webArticleSummariseQuery.py --url "https://example.com/article" --model "your_desired_model" [--api "your_desired_api"] [--port 5001]
```

The API will be available at `http://localhost:5001`. You can make POST requests to `/summarize` or `/query` endpoints, providing the required parameters in JSON format.

For example, using a tool like `curl`:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"url": "https://example.com/article", "model": "your_desired_model"}' http://localhost:5001/summarize
```