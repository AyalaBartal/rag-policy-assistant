from __future__ import annotations

import os

from dotenv import load_dotenv
from openai import OpenAI

from src.rag.rag_pipeline import RagPipeline


def main() -> None:
    load_dotenv()

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set.")

    model_name = os.getenv("OPENROUTER_MODEL", "openrouter/free")

    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    pipeline = RagPipeline(llm_client=client, model_name=model_name)

    print("\nRAG Policy Assistant")
    print("Type 'exit' to quit\n")

    while True:
        question = input("Ask a question: ").strip()

        if question.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not question:
            continue

        result = pipeline.answer(question)

        print("\nAnswer:\n")
        print(result.answer)

        if result.citations:
            print("\nSources:")
            for citation in result.citations:
                print(f"- {citation}")

        print("\n" + "-" * 80 + "\n")


if __name__ == "__main__":
    main()