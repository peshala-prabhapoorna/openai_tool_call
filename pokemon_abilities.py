import requests


get_pokemon_abilities_tool_schema = {
    "type": "function",
    "name": "get_pokemon_abilities",
    "description": "Get information about the abilities of a Pokemon with the given name",
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


def get_pokemon_abilities(name: str):
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name.lower()}/")
    return response.json()["abilities"]
