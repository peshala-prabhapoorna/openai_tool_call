import json
import os
from typing import Iterable

from dotenv import load_dotenv
from openai import NotGiven, OpenAI
from openai.types.responses.function_tool_param import FunctionToolParam
from openai.types.responses.response_create_params import ToolChoice
from openai.types.responses.response_function_tool_call import ResponseFunctionToolCall
from openai.types.responses.response_input_param import ResponseInputParam
from openai.types.responses.response_output_message import ResponseOutputMessage
from openai.types.responses.response_output_text import ResponseOutputText
from openai.types.responses.tool_param import ToolParam
from tenacity import retry, stop_after_attempt, wait_random_exponential
from termcolor import colored

from pokemon import get_pokemon, get_pokemon_tool_schema


GPT_MODEL = "gpt-4.1"

load_dotenv()
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def generate_response(
    message: ResponseInputParam | NotGiven,
    tools: Iterable[ToolParam] | NotGiven,
    tool_choice: ToolChoice | NotGiven,
    model=GPT_MODEL
):
    try:
        response = client.responses.create(
            model=model,
            input=message,
            tools=tools,
            tool_choice=tool_choice
        )
        return response
    except Exception as e:
        print("Unable to generate response")
        print(f"Exception: {e}")
        return e


def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assitant": "blue",
        "function": "magenta"
    }

    for message in messages:
        if message["role"] == "system":
            print(colored(f"system: {message["content"]}\n", role_to_color[message["role"]]))
        elif message["role"] == "user":
            print(colored(f"user: {message["content"]}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and message.get("function_call"):
            print(colored(f"assistant: {message["function_call"]}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and not message.get("function_call"):
            print(colored(f"assistant: {message["content"]}\n", role_to_color[message["role"]]))
        elif message["role"] == "function":
            print(colored(f"function {message["name"]}: {message["content"]}\n", role_to_color[message["role"]]))


tools = [FunctionToolParam(**get_pokemon_tool_schema)]

system_message = {
    "role": "system",
    "content": "Don't make assumptions about what values to plug into the functions. Ask for clarification if a user request is ambigious.",
}

messages = []
messages.append(system_message)
print(f"💡 {colored("I'm a smart cookie. As me anything...", "green")}")
while True:
    user_input = input(f"🐳 {colored("How can I help you?", "green")} ")
    if user_input == "exit":
        print(f"👋🏼 {colored("Bye bye...", "magenta")}")
        exit()
    user_message = {
        "role": "user",
        "content": user_input,
    }
    messages.append(user_message)

    response = generate_response(
        message=messages,
        tools=tools,
        tool_choice="auto",
    )

    if isinstance(response, Exception):
        exit()

    tool_call = []
    for output in response.output:
        if isinstance(output, ResponseFunctionToolCall):
            tool_call.append(output)
        elif isinstance(output, ResponseOutputMessage):
            content = output.content[0]
            if isinstance(content, ResponseOutputText):
                print(content.text)
            continue

    for call in tool_call:
        if call.name == "get_pokemon":
            args = json.loads(call.arguments)

            results = get_pokemon(args["name"])

            messages.append(call)

            messages.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": str(results)
            })

        response_2 = generate_response(
            message=messages,
            tools=tools,
            tool_choice="auto",
        )
        if not isinstance(response_2, Exception):
            print(response_2.output_text)
