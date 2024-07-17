import argparse
import requests
import logging
from flask import Flask, request, jsonify
from llm_chat_api import LLMChatAPI

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

def fetch_article_content(url):
    try:
        logging.info(f"Fetching article content from {url}")
        response = requests.get(f"https://r.jina.ai/{url}")
        response.raise_for_status()
        logging.info("Successfully fetched article content from jina.ai")
        return response.text
    except requests.RequestException as e:
        logging.error(f"Failed to fetch article content: {e}")
        raise

def summarize_article(content, llm_api, model, callback=None, messages=None):
    if not messages:
        messages = [
            {
                "role": "system",
                "content": (
                    "Summarise the provided article. If it is a transcript of an interview, please say so. "
                    "Introduce the key authors, speakers, characters or interviewers and their titles and/or roles. "
                    "Articulate their points of view, key themes, concerns and arguments in point form, and by the person who has mentioned it."
                )
            },
            {"role": "user", "content": f"Please summarize the following article: {content}"}
        ]
    return llm_api.chat_completions(messages, model=model, temperature=0.1, stream=True, callback=callback)

def query_article(content, question, llm_api, model, callback=None, messages=None):
    if not messages:
        messages = [
            {"role": "system", "content": "You are a helpful assistant that answers questions based on articles."},
            {"role": "user", "content": f"Here is the article: {content}"},
            {"role": "user", "content": f"Question: {question}"}
        ]
    return llm_api.chat_completions(messages, model=model, temperature=0.1, stream=True, callback=callback)

def summarize_and_query_article(url, model, api_identifier="lmstudio", question=None, messages=None):
    llm_api = LLMChatAPI(api_identifier)
    article_content = fetch_article_content(url)
    
    def handle_chunk(chunk, end=False):
        # Custom handling of each chunk
        if chunk:
            print(chunk, end='', flush=True)
        if end:
            print()  # Print a newline at the end of the stream

    logging.info(f"Processing article with model {model} using API {api_identifier}")
    
    if question:
        result = query_article(article_content, question, llm_api, model, callback=handle_chunk, messages=messages)
    else:
        result = summarize_article(article_content, llm_api, model, callback=handle_chunk, messages=messages)
    
    if not result:
        logging.error("Failed to get a response from the LLM.")
    return result

@app.route('/summarize', methods=['POST'])
def api_summarize():
    data = request.json
    url = data.get('url')
    model = data.get('model')
    api_identifier = data.get('api', 'lmstudio')
    if not url or not model:
        return jsonify({"error": "URL and model are required"}), 400
    try:
        result = summarize_and_query_article(url, model=model, api_identifier=api_identifier)
        return jsonify({"summary": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/query', methods=['POST'])
def api_query():
    data = request.json
    url = data.get('url')
    model = data.get('model')
    question = data.get('question')
    api_identifier = data.get('api', 'lmstudio')
    if not url or not model or not question:
        return jsonify({"error": "URL, model, and question are required"}), 400
    try:
        result = summarize_and_query_article(url, model=model, api_identifier=api_identifier, question=question)
        return jsonify({"answer": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def main():
    parser = argparse.ArgumentParser(description="Summarize or query an article from a URL.")
    parser.add_argument("url", type=str, help="The URL of the article to process.")
    parser.add_argument("--summarize", action="store_true", help="Summarize the article.")
    parser.add_argument("--query", type=str, help="Query the article with a specific question.")
    parser.add_argument("--api", type=str, default="lmstudio", help="API identifier to use (default: lmstudio).")
    parser.add_argument("--model", type=str, required=True, help="The LLM model to use.")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the Flask server on (default: 5000).")
    
    args = parser.parse_args()

    if args.summarize or args.query:
        if args.summarize:
            summarize_and_query_article(args.url, model=args.model, api_identifier=args.api)
        elif args.query:
            summarize_and_query_article(args.url, model=args.model, api_identifier=args.api, question=args.query)
    else:
        print("Please specify either --summarize or --query 'your question'.")
        app.run(host='0.0.0.0', port=args.port)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        main()
    else:
        app.run(host='0.0.0.0', port=5001)
