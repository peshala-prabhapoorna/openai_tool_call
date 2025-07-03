import requests


get_pokemon_tool_schema = {
    "type": "function",
    "name": "get_pokemon",
    "description": "Get information about a Pokemon with the given name",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of a Pokemon. eg: Pikachu, Bulbasaur"
            }
        },
        "required": [
            "name"
        ],
        "additionalProperties": False
    }
}


def get_pokemon(name: str):
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name.lower()}/")
    return response.json()["abilities"]
