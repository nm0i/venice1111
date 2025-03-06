#!/bin/env python3

import os

import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict

load_dotenv()

app = FastAPI()

VENICE_KEY = os.getenv("VENICE_KEY")

VENICE_BASEURI = "https://api.venice.ai/"
VENICE_DEFAULT_MODEL = "fluently-xl"
VENICE_PROMPT_CUTOUT = 1024
VENICE_IMAGE_XY_CUTOUT = 1280


class VeniceOptions(BaseModel):

    model_config = ConfigDict(extra="ignore")

    sd_model_checkpoint: str = VENICE_DEFAULT_MODEL
    samples_format: str = "png"


class VeniceT2IParams(BaseModel):

    model_config = ConfigDict(extra="ignore")

    prompt: str
    negative_prompt: str = ""
    steps: int = 30
    cfg_scale: float = 7.0
    seed: int = -1
    width: int = 1024
    height: int = 1024
    override_settings: dict


venice_options = VeniceOptions()


@app.get("/sdapi/v1/sd-models")
async def read_models():

    url = f"{VENICE_BASEURI}api/v1/models?type=image"

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


@app.get("/sdapi/v1/sd-vae")
async def read_vae():

    url = f"{VENICE_BASEURI}api/v1/image/styles"

    headers = {"Authorization": f"Bearer {VENICE_KEY}"}

    response = requests.request("GET", url, headers=headers)

    if response.status_code == 200:
        styles_list = []
        for i in response.json()["data"]:
            style = {
                "model_name": i,
            }
            styles_list.append(style)
        return styles_list
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


@app.get("/sdapi/v1/progress")
async def read_progess():
    return {"progress": 0.0, "state": {"job_count": 0}}


@app.post("/sdapi/v1/txt2img")
async def serve_t2i(params: VeniceT2IParams):

    url = f"{VENICE_BASEURI}api/v1/image/generate"

    if params.width > VENICE_IMAGE_XY_CUTOUT:
        params.width = VENICE_IMAGE_XY_CUTOUT
    if params.height > VENICE_IMAGE_XY_CUTOUT:
        params.height = VENICE_IMAGE_XY_CUTOUT

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

    if params.override_settings and params.override_settings["sd_vae"]:
        payload["style_preset"] = params.override_settings["sd_vae"]

    headers = {
        "Authorization": "Bearer " + VENICE_KEY,
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
        print
        raise HTTPException(
            status_code=400,
            detail=f"Error accessing venice api: {response.text}.",
        )


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=9900, log_level="debug")
