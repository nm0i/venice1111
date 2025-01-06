import os

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Extra

load_dotenv()

app = FastAPI()

VENICE_BASEURI = "https://api.venice.ai/"
VENICE_DEFAULT_MODEL = "fluently-xl"
VENICE_KEY = os.getenv("VENICE_KEY")
VENICE_PROMPT_CUTOUT = 1024


class VeniceOptions(BaseModel):
    sd_model_checkpoint: str = VENICE_DEFAULT_MODEL
    samples_format: str = "png"

    class Config:
        extra = Extra.ignore


class VeniceT2IParams(BaseModel):
    prompt: str
    negative_prompt: str = ""
    steps: int = 25
    cfg_scale: int = 7
    seed: int = 0
    width: int = 1024
    height: int = 1024

    class Config:
        extra = Extra.ignore


venice_options = VeniceOptions()


@app.get("/sdapi/v1/sd-models")
async def read_models():

    url = f"{VENICE_BASEURI}api/v1/models"

    headers = {"Authorization": f"Bearer {VENICE_KEY}"}

    response = requests.request("GET", url, headers=headers)

    if response.status_code == 200:
        model_list = []
        for i in response.json()["data"]:
            if i["type"] != "image":
                continue

            model = {
                "title": i["id"],
                "model_name": i["id"],
                "hash": "8888888888",
                "sha256": "8888888888888888888888888888888888888888888888888888888888888888",
                "config": None,
            }
            model_list.append(model)
        return model_list
    else:
        raise HTTPException(
            status_code=400, detail="Error accessing venice api."
        )


@app.post("/sdapi/v1/options")
async def write_options(params: VeniceOptions):
    venice_options.sd_model_checkpoint = params.sd_model_checkpoint
    return venice_options.dict()


@app.get("/sdapi/v1/options")
async def read_options():
    return venice_options.dict()


@app.get("/sdapi/v1/samplers")
async def read_samplers():
    return [
        {
            "name": "Euler",
            "aliases": [
                "euler",
            ],
            "options": {},
        },
    ]


@app.get("/sdapi/v1/progress")
async def read_progess():
    return {"progress": 0.0, "state": {"job_count": 0}}


@app.post("/sdapi/v1/txt2img")
async def serve_t2i(params: VeniceT2IParams):

    url = f"{VENICE_BASEURI}api/v1/image/generate"

    payload = {
        "model": venice_options.sd_model_checkpoint,
        "prompt": params.prompt[:VENICE_PROMPT_CUTOUT],
        "negative_prompt": params.negative_prompt[:VENICE_PROMPT_CUTOUT],
        "width": params.width,
        "height": params.height,
        "steps": params.steps,
        "hide_watermark": True,
        "return_binary": False,
    }

    headers = {
        "Authorization": "Bearer " + os.getenv("VENICE_KEY"),
        "Content-Type": "application/json",
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    if response.status_code == 200:
        return {
            "images": response.json()["images"],
            "parameters": {},
            "info": "",
        }
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Error accessing venice api: {response.text}.",
        )
