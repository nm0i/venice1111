# Venice1111

FastAPI proxy for <Venice.AI> image generation API that presents itself as [AUTOMATIC1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui) endpoint.

This proxy should allow image generation via compatible API tools, such as StableUI, SillyTavern, KoboldAI.

## Installing

    git clone https://github.com/nm0i/venice1111.git
    cd venice1111
    python3 -m venv venv
    . ./venv/bin/activate
    pip install -r requirements.txt

## Running

    . ./venv/bin/activate
    VENICE_KEY=<your_api_key> uvicorn venice1111:app --host 127.0.0.1 --port 9900 --reload

Then connect your app to http://127.0.0.1:9900.

## Note

DO NOT serve this API over untrusted networks:
 - <Venice.ai> restricts both concurrent requests and total images per day.
 - Something about security.
