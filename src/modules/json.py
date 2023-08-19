import os
import requests
import json

def load_json(name, url):
    # Check if the .presets folder exists, if not, create it
    presets_folder = "json.data"
    if not os.path.exists(presets_folder):
        os.makedirs(presets_folder)
    json_url = url
    json_options_file_path = os.path.join(presets_folder, name)

    try:
        response = requests.get(json_url, timeout=5)
        response.raise_for_status()

        data = response.json()

        if os.path.exists(json_options_file_path):
            with open(json_options_file_path, "r") as file:
                local_json_options = json.load(file)

            if data != local_json_options:
                with open(json_options_file_path, "w") as file:
                    json.dump(data, file)
                    json_options = data
            else:
                json_options = local_json_options
        else:
            with open(json_options_file_path, "w") as file:
                json.dump(data, file)
                json_options = data

    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"Error occurred while fetching or parsing Description.json: {e}")
        if os.path.exists(json_options_file_path):
            with open(json_options_file_path, "r") as file:
                json_options = json.load(file)
        else:
            json_options = []

    return json_options