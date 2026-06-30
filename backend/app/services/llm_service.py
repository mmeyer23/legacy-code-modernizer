from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client: OpenAI | None = None


def get_openai_client() -> OpenAI:
    global client

    if client is not None:
        return client

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is required to call the LLM service. "
            "Set OPENAI_API_KEY before running analysis or migration."
        )

    client = OpenAI(api_key=api_key)
    return client


def analyze_code(prompt: str) -> str:
    response = get_openai_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a senior software engineer specializing in legacy systems. "
                    "You analyze Fortran code and explain it clearly for migration to Python."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content
