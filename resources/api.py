# resources/base.py
import aiohttp
from controllers.utility import Config

config = Config()
API_URL = config.get("api")
HEADERS = {}

if config.get("debug"): # When testing locally, we use ngrok for tunneling
    HEADERS["ngrok-skip-browser-warning"] = "revyena-trusted-origin"

async def request(method: str, path: str, model=None, **kwargs):
    url = f"{API_URL}{path}"
    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, headers=HEADERS, **kwargs) as resp:
            resp.raise_for_status()
            data = await resp.json()
            if model:
                return model.from_dict(data)
            return data

async def get(path: str, model=None, **kwargs):
    return await request("GET", path, model=model, **kwargs)

async def post(path: str, model=None, **kwargs):
    return await request("POST", path, model=model, **kwargs)
