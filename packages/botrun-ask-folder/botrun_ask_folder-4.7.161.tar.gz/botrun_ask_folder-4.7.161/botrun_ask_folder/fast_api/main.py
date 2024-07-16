from fastapi import FastAPI
from botrun_ask_folder.fast_api.router_botrun_ask_folder import router
app = FastAPI()
api_botrun = FastAPI()


api_botrun.include_router(router)
app.mount("/api/botrun", api_botrun)
