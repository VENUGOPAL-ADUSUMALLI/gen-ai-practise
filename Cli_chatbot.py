import os
from dotenv import load_dotenv
from openai import OpenAI, max_retries
from google import genai
load_dotenv()
import time

openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

gemini_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def call_openai(user_input):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            stream = openai_client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {
                        "role": "user",
                        "content": user_input
                    }
                ],
                stream=True,
                stream_options={
                    "include_usage": True
                }
            )
            full_response = ""
            usage = None
            print("OpenAI: ", end="", flush=True)
            for chunk in stream:
                if chunk.choices:
                    content = chunk.choices[0].delta.content

                if content:
                    print(content, end="", flush=True)
                    full_response += content
                if chunk.usage:
                    usage = chunk.usage

            print()
            if usage:
                print(
                    f"Tokens → "
                    f"Input: {usage.prompt_tokens}, "
                    f"Output: {usage.completion_tokens}, "
                    f"Total: {usage.total_tokens}"
                )
            return full_response
        except Exception as e:
            print(f"openai failed with {attempt + 1} /{max_retries}")
            if attempt == max_retries-1:
                raise  e
            delay = 2 ** attempt
            print(f"retrying in {delay} second, attempt {attempt+1}")
            time.sleep(delay)



def call_gemini(user_input):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            stream = gemini_client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=user_input
            )
            full_response = ""
            usage = None
            print("Gemini: ", end="", flush=True)

            for chunk in stream:
                if chunk.text:
                    print(chunk.text, end="", flush=True)
                    full_response += chunk.text
                if chunk.usage_metadata:
                    usage = chunk.usage_metadata
            print()
            if usage:
                print(
                    f"Tokens → "
                    f"Input: {usage.prompt_token_count}, "
                    f"Output: {usage.candidates_token_count}, "
                    f"Total: {usage.total_token_count}"
                )
            return full_response
        except Exception as e:
            print(
                f"\nGemini attempt {attempt + 1}/{max_retries} failed"
            )
            if attempt == max_retries - 1:
                raise e
            delay = 2 ** attempt
            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)

while True:
    print("ASK Question:")
    user_input = input()

    if user_input.lower() in ["exit", "quit", "stop"]:
        break
    try:
        openai_response = call_openai(user_input)
    except  Exception as e:
        print("open ai failed")
        print("Error", e)
        print("Falling back to gemini")
        gemini_response = call_gemini(user_input)
