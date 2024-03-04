from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(base_url="http://localhost:8680/v1")

if __name__ == "__main__":
    res = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt="Hello --> こんにちは\nI love The Lord of the Rings -->",
        stream=True,
        max_tokens=80,
        stop=["\n"],
    )
    for chunk in res:
        for choice in chunk.choices:
            if choice.text:
                print(choice.text, end="", flush=True)
    print()
