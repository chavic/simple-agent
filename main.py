import argparse
import os

from dotenv import load_dotenv
from openai import OpenAI

from call_function import available_functions, call_function
from prompts import system_prompt


def run_agent(
    client: OpenAI,
    messages: list,
    verbose: bool = False,
    max_iterations: int = 20,
) -> bool:
    for _ in range(max_iterations):
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=messages,
            temperature=0,
            tools=available_functions,
        )

        if verbose and response.usage:
            print(f"Prompt tokens: {response.usage.prompt_tokens}")
            print(f"Response tokens: {response.usage.completion_tokens}")

        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            print(f"Final response:\n{message.content}")
            return True

        for tool_call in message.tool_calls:
            result_message = call_function(tool_call, verbose)
            if not result_message.get("content"):
                raise RuntimeError("Function call returned empty content")
            if verbose:
                print(f"-> {result_message['content']}")
            messages.append(result_message)

    print(
        f"Error: Agent did not produce a final response after "
        f"{max_iterations} iterations"
    )
    return False


def main() -> None:
    load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")

    if not api_key:
        raise RuntimeError("API key not found")

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose output"
    )
    args = parser.parse_args()

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    messages: list = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt},
    ]

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")

    if not run_agent(client, messages, args.verbose):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
