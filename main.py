import json
import logging.config
import os
import uuid
from datetime import datetime, timezone

import redis.asyncio as redis

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from common_dto import OrderDto


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGGING_CONFIG = os.path.join(BASE_DIR, 'logging.ini')

logging.config.fileConfig(LOGGING_CONFIG, defaults=None)
logger = logging.getLogger(__file__)

# logger.debug('debug message')
# logger.info('info message')
# logger.error('error message')
# logger.critical('critical message')

load_dotenv('.env', verbose=True, override=True)

app = FastAPI()
r_orders = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=os.environ.get("REDIS_PORT", "6379"), db=0)
r_session = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=os.environ.get("REDIS_PORT", "6379"), db=1)

JSON_LIMIT_SIZE = 16000


@app.post("/get-session/")
async def register_user():
    session_id = str(uuid.uuid4())
    try:
        await r_session.set(session_id, "Active")
        logger.info(f"Successfully obtained session id for user")
        return {"session_id": session_id}
    except Exception as e:
        logger.error(f"Error while obtaining session id, probably lost connection to redis\n {e}")
        raise HTTPException(status_code=500, detail="internal server error")


@app.get("/order/")
async def read_item_by_hash_name(json_data: str, session_id: str, client_order_id: str):
    exist_check_session = await r_session.exists(session_id)
    exist_check_client_order_id = await r_orders.exists(client_order_id)

    logger.info(exist_check_session)

    if not exist_check_session:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if len(json_data) >= JSON_LIMIT_SIZE:
        raise HTTPException(status_code=413, detail=f"too big json data, {JSON_LIMIT_SIZE} limit")

    order = OrderDto

    server_time = datetime.now(timezone.utc)
    order_id = str(uuid.uuid4())

    try:
        data = json.loads(json_data)
        data["server_time"] = server_time.isoformat()
        data["order_id"] = order_id
        data["session_id"] = session_id


    except json.JSONDecodeError as e:
        logger.error(f"JSON format error during serialization: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid JSON format provided.")
    except Exception as e:
        logger.error(f"Unhandled exception during JSON serialization: {str(e)}")
        raise HTTPException(status_code=500, detail="error during data processing.")

    order.json_body = data

    if not exist_check_client_order_id:
        try:
            r_orders.set(client_order_id, json.dumps(order.json_body))
        except Exception as e:
            logger.error(f"Got error during writing into redis, probably lost connection\n{e}")
            raise HTTPException(status_code=500, detail="internal server error")
    else:
        logger.info("Attemp to add already existing order, nothing to do")
    return {"order_id": order_id}


if __name__ == '__main__':
    redis_host = os.environ.get("REDIS_HOST", "localhost")
    logger.info(f"redis_host={redis_host}")

    uvicorn.run(app, host="localhost", port=8000)
