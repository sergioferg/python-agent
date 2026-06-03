import argparse
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


def main():
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable not set")

    client  = genai.Client(api_key=api_key)
    messages: list[types.Content] = [
        types.Content(role="user", parts=[types.Part(text=args.user_prompt)])
    ]
    generate_content(client, messages)


def generate_content(client: genai.Client, messages: list[types.Content]) -> None:
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=messages,
    )
    if not response.usage_metadata:
        raise RuntimeError("Gemini API response has encountered an error")

    print("Prompt tokens:", response.usage_metadata.prompt_token_count)
    print("Response tokens:", response.usage_metadata.candidates_token_count)
    print("Response:")
    print(response.text)

if __name__ == "__main__":
    main()
