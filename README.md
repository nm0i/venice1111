# Venice1111

FastAPI proxy for [Venice.AI](https://venice.ai/) image generation API that presents itself as [AUTOMATIC1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui) endpoint.

This proxy should allow image generation via compatible API tools.

## Installing

    git clone https://github.com/nm0i/venice1111.git
    cd venice1111
    python3 -m venv venv
    . ./venv/bin/activate
    pip install -r requirements.txt
    exit

## Running

    . ./venv/bin/activate
    VENICE_KEY=<your_api_key> ./main.py

Alternatively, you can save your key in `.env` file as `VENICE_KEY=<your_api_key>`

Then connect your app to http://127.0.0.1:9900.

## Note

DO NOT serve this API over untrusted networks:
 - <Venice.ai> restricts both concurrent requests and total images per day.
 - Something about security.
