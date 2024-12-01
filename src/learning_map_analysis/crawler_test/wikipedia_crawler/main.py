import subprocess
from fastapi import FastAPI
import json


app = FastAPI()


@app.get("/{search_item}")
async def root(search_item):
    subprocess.call([f'python app.py {search_item}'], shell=True)
    with open("visualisation_data_graph.json", "r") as f:
        return json.load(f)