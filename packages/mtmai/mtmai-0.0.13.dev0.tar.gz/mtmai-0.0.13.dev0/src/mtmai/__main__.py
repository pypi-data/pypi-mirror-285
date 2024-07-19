from . import hello_world

# if __name__ == '__main__':
#     hello_world()

import logging
from os.path import join, dirname
from fastapi import FastAPI
import inngest
import inngest.fast_api
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from __version__ import version, title, description

from ._version import version
from .routes import health, completion,classifyDemo1
from dotenv import load_dotenv
import uvicorn
from .app import app

load_dotenv()  # take environment variables from .env.

dotenv_path = join(dirname(__file__), '../../env/dev.env')
load_dotenv(dotenv_path)

## 开发环境启动方式：
##   (INNGEST_DEV=1 uvicorn main:app --reload --host 0.0.0.0 --port 8201)


inngest_client = inngest.Inngest(
    app_id="mtai",
    logger=logging.getLogger("uvicorn"),
)

# Create an Inngest function
@inngest_client.create_function(
    fn_id="mtai/hello",
    # Event that triggers this function
    trigger=inngest.TriggerEvent(event="mtai/hello"),
)
async def my_function(ctx: inngest.Context, step: inngest.Step) -> str:
    ctx.logger.info("hello run python -----------------------")
    ctx.logger.info(ctx.event)
    return "done"

# app = FastAPI(
#     # title=title,
#     version=version,
#     # description=description,
#     # root_path=root_path,
# )
# origins = ["*"]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# app.include_router(health.router)
# app.include_router(completion.router)
# app.include_router(classifyDemo1.router)

# @app.on_event("startup")
# async def startup_event():
#     print("mtmai 后端 http 服务启动")
# @app.get("/")
# async def root():
#     return {"message": "Hello World22"}

if __name__ == "__main__":
    hello_world()
    # Serve the Inngest endpoint
    inngest.fast_api.serve(app, inngest_client, [my_function])
    uvicorn.run(app, port=8000)
