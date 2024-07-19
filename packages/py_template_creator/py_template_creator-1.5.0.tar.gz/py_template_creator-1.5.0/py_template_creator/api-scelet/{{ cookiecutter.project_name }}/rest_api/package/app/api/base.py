from fastapi import APIRouter

base_router = APIRouter()


@base_router.get("/", tags=["root"])
async def read_root() -> dict:
    return {"msg": "Welcome!", "status": "OK"}


@base_router.get("/health", tags=["health"])
async def health() -> dict:
    return {"msg": "API is working correctly", "status": "OK"}
