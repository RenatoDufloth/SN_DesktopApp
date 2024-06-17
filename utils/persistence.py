# Version 1.0: Implementação Inicial
import os
import json

CACHE_DIR = 'data/cache'

def load_cache(directory):
    cache_data = {}
    if not os.path.exists(directory):
        os.makedirs(directory)
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), 'r') as file:
                data = json.load(file)
                prefix = filename[:-5]  # Remove '.json' extension
                cache_data[prefix] = data
    return cache_data

def save_cache(cache_data):
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    for prefix, data in cache_data.items():
        with open(os.path.join(CACHE_DIR, f"{prefix}.json"), 'w') as file:
            json.dump(data, file, indent=4)
