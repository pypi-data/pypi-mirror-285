import requests
import json
import logging
from requests.exceptions import RequestException, HTTPError
from openai import OpenAI

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")


class LLMChatAPI:
    def __init__(self, api_identifier, retry_attempts=3, default_model=None):
        self.api_identifier = api_identifier
        self.base_url = self._get_base_url(api_identifier)
        self.retry_attempts = retry_attempts
        if default_model:
            self.default_model = default_model
        else:
            self.default_model = self._get_default_model(api_identifier)
        logging.basicConfig(level=logging.INFO)

        if api_identifier == "lmstudio":
            self.client = OpenAI(base_url=self.base_url, api_key="lm-studio")

    def _get_base_url(self, api_identifier):
        base_url_mapping = {
            "lmstudio": "http://localhost:1234/v1",
            "ollama": "http://localhost:11434/api/chat"
            # Add more mappings as needed
        }
        return base_url_mapping.get(api_identifier, "http://localhost:1234/v1")

    def _get_default_model(self, api_identifier):
        default_model_mapping = {
            "lmstudio": "lmstudio-community/Mistral-7B-Instruct-v0.3-GGUF",
            "ollama": "mistral"
        }
        return default_model_mapping.get(api_identifier, "lmstudio-community/Mistral-7B-Instruct-v0.3-GGUF")

    def _make_request(self, url, headers, payload, stream):
        attempt = 0
        while attempt < self.retry_attempts:
            try:
                response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10, stream=stream)
                response.raise_for_status()  # Raises HTTPError for bad responses
                return response
            except (RequestException, HTTPError) as e:
                attempt += 1
                logging.warning(f"Attempt {attempt} failed: {e}. Retrying...")
        raise RequestException("All retry attempts failed.")

    def chat_completions(self, messages, model=None, temperature=0.7, max_tokens=-1, stream=True, callback=None, **kwargs):
        if model is None:
            model = self.default_model

        if self.api_identifier == "lmstudio":
            return self._lmstudio_chat_completions(messages, model, temperature, max_tokens, stream, callback, **kwargs)
        else:
            url = self.base_url
            headers = {
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream
            }
            payload.update(kwargs)  # Add any additional parameters to the payload

            try:
                response = self._make_request(url, headers, payload, stream)
                if stream:
                    return self._handle_streaming_response(response, callback)
                else:
                    response_json = response.json()
                    if 'choices' in response_json:
                        # lmstudio response format
                        content = response_json['choices'][0]['message']['content']
                    elif 'message' in response_json:
                        # ollama response format
                        content = response_json['message']['content']
                    else:
                        logging.error(f"Unexpected response format: {response_json}")
                        raise ValueError("Unexpected response format")
                    return content
            except RequestException as e:
                logging.error(f"Failed to get a response: {e}")
            except ValueError as e:
                logging.error(f"Failed to parse response: {e}")

    def _lmstudio_chat_completions(self, messages, model, temperature, max_tokens, stream, callback, **kwargs):
        try:
            completion = client.chat.completions.create(model=model,
                                                            messages=messages,
                                                            temperature=temperature,
                                                            max_tokens=max_tokens,
                                                            stream=stream)
            if stream:
                return self._handle_lmstudio_streaming_response(completion, callback)
            else:
                return completion.choices[0].message
        except Exception as e:
            logging.error(f"Failed to get a response from lmstudio: {e}")

    def _handle_lmstudio_streaming_response(self, response, callback=None):
        content = ""
        for chunk in response:
            chunk_content = chunk.choices[0].delta.content
            if chunk_content is not None:
                if callback:
                    callback(chunk_content)
                content += chunk_content
            # else:
            #     logging.warning("Received None content in chunk")
        if callback:
            callback('', end=True)
        return content

    def _handle_streaming_response(self, response, callback=None):
        content = ""
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8').strip()
                if decoded_line.startswith("data: "):
                    decoded_line = decoded_line[len("data: "):]
                try:
                    json_line = json.loads(decoded_line)
                    if 'message' in json_line and 'content' in json_line['message']:
                        chunk = json_line['message']['content']
                        if chunk is not None:
                            if callback:
                                callback(chunk)
                            content += chunk
                        # else:
                        #     logging.warning("Received None content in stream line")
                except json.JSONDecodeError as e:
                    logging.warning(f"Failed to decode line: {decoded_line} - Error: {e}")
        if callback:
            callback('', end=True)
        return content


# Usage example
if __name__ == "__main__":

    def handle_chunk(chunk, end=False):
        # Custom handling of each chunk
        if chunk:
            print(chunk, end='', flush=True)
        if end:
            print()  # Print a newline at the end of the stream

    lm_studio_llm_api = LLMChatAPI("lmstudio")
    ollama_llm_api = LLMChatAPI("ollama")
    
    messages = [
        { "role": "system", "content": "Always answer in rhymes." },
        { "role": "user", "content": "Introduce yourself." }
    ]
    
    lm_studio_response = lm_studio_llm_api.chat_completions(
        messages, 
        model="lmstudio-community/Mistral-7B-Instruct-v0.3-GGUF", 
        temperature=0.7, 
        max_tokens=-1, 
        stream=True,
        callback=handle_chunk    
    )

    # ollama_response = ollama_llm_api.chat_completions(
    #     messages,
    #     model="mistral", 
    #     stream=True,
    #     callback=handle_chunk  # Use the custom callback to handle streaming chunks
    # )

    # if lm_studio_response:
    #     print("lm_studio_response:", lm_studio_response)

    # if ollama_response:
    #     print("ollama_response:", ollama_response)
