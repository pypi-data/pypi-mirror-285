from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from plutous.config import config

if config.sentry_dsn:
    import sentry_sdk

    sentry_sdk.init(config.sentry_dsn)

app = FastAPI(
    title="Plutous API",
    version="0.0.1",
)

try:
    from plutous.trade.app.main import app as trade

    app.mount("/trade", trade)
except ImportError:
    pass


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Hello from Plutous API"}
