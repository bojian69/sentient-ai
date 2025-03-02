from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel
import uuid
import os, asyncio, json
from together import AsyncTogether
from sentient import sentient
from dotenv import load_dotenv
import redis.asyncio as aioredis

load_dotenv()

app = FastAPI()

redis_prefix = 'selenium:chat:message'


class RequestData(BaseModel):
    goal: str
    model: str


@app.get("/")
async def read_root():
    return {"message": "Hello, World"}


@app.get("/chat/async/models")
async def model():
    return {'models': [
        {'model': 'mistralai/Mixtral-8x7B-Instruct-v0.1', 'label': 'Mixtral-8x7B-Instruct-v0.1:自然语言处理模型'},
        {'model': 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo', 'label': 'Llama-3.1-70B-Instruct-Turbo:指令模型'},
    ]}


@app.post("/chat/async/submit")
async def submit(goal: str = Form(...), model: str = Form(...)):
    uuid_str = str(uuid.uuid4())
    print('TOGETHER_API_KEY:', os.environ.get("TOGETHER_API_KEY"))
    async_client = AsyncTogether(api_key=os.environ.get("TOGETHER_API_KEY"))
    message = ''
    # 切换检索模型
    if model == 'mistralai/Mixtral-8x7B-Instruct-v0.1':
        try:
            response = await async_client.chat.completions.create(
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                messages=[{"role": "user", "content": goal}],
            )
            message = response.choices[0].message.content
        except Exception as e:
            message = str(e)
            print(message)
    elif model == 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo':
        try:
            message = await sentient.invoke(
                goal=goal,
                provider="together",
                model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo")
        except Exception as e:
            message = str(e)
            print(message)

    # message 数据存入 Redis
    redis = aioredis.from_url('redis://localhost', decode_responses=True)
    await redis.set(
        name=f'{redis_prefix}:{uuid_str}',
        value=json.dumps({'goal': goal, 'message': message, 'model': model}, ensure_ascii=False),
        ex=3600 * 24 * 7
    )
    await redis.close()

    return {"message": message, "model": model, "uuid": uuid_str}


@app.post("/chat/async/message")
async def message(uuid: str = Form(...)):
    # message 数据存入 Redis
    redis = aioredis.from_url('redis://localhost', decode_responses=True)
    response = await redis.get(name=f'{redis_prefix}:{uuid}')
    await redis.close()

    if response is None:
        raise HTTPException(status_code=404, detail="Message not found")
    response = json.loads(response)
    return {
        'goal': response['goal'], 
        'message': response['message'],
        'model': response['model'],
        'uuid': uuid
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
