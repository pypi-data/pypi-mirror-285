import sys

import vertexai

from vertexai.generative_models import (
    GenerativeModel,
)

import argparse


def generate_client():

    system_instruction = [
        "User will provide instruction and context where this instruction will be applied. Output will be sent to a bash pipe so your output should NOT have any explanations or anything, just the required operations.",
        "If you are asked to update something, you need to show the same data structure but updated, in the same format. Do not show HOW to update the data structure, just update it and output the result.",
        "Here is how you might be used by the user: cat file | you -p \"prompt\" >> result",
        "If you are asked to generate something like JSON or other files, output the result without surrounding it with ```json ... ``` or any other characters. Your output should be usable as is."
    ]

    vertexai.init()

    return GenerativeModel(model_name="gemini-1.5-pro", system_instruction=system_instruction)


gemini_model = generate_client()


def main():
    parser = argparse.ArgumentParser(description='Toolbox for using Gemini Agents SDK.')
    parser.add_argument('-p', '--prompt', type=str, required=True, help='The prompt for the Gemini model.')
    args = parser.parse_args()

    msg = f"User provided prompt: {args.prompt}"
    if not sys.stdin.isatty():
        lines = "".join([line for line in sys.stdin])

        msg = f"""User provided prompt: {args.prompt} 
---
User provided content:
{lines}"""
    print(gemini_model.generate_content(msg).text)
