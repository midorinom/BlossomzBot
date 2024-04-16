import aiohttp
from config import config_values

url = config_values["sheetdb_url"]

async def create_in_holding_area(payload):
    try:
        payload = {
            "data": payload,
            "sheet": "Holding Area"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as res:
                response = await res.json()
                return response
            
    except Exception:
        print("An error occurred in 'create_in_holding_area'.")
        raise 
