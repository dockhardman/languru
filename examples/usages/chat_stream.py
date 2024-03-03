from openai import OpenAI

client = OpenAI(base_url="http://localhost:8680/v1")


if __name__ == "__main__":
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ],
        stream=True,
    )
    for chunk in res:
        for choice in chunk.choices:
            if choice.delta.content:
                print(choice.delta.content, end="", flush=True)
