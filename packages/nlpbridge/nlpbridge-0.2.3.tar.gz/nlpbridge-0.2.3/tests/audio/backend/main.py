from config import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tests.audio.backend.api import router

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")
app.include_router(router, prefix=settings.API_V1_STR)
# 允许所有来源的CORS请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    print("\nAvailable endpoints:")
    for route in app.routes:
        path = route.path
        print(f"{path}")


def main():
    import argparse
    import uvicorn
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="The host to run the server", default="127.0.0.1")
    parser.add_argument("--port", help="The port to run the server", default=9999)
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
