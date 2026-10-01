import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse

from app.database import (
    create_item,
    get_item,
    get_items,
    initialize_database,
    seed_database,
    update_item,
    delete_item,
)

from app.models import ItemCreate, ItemUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    seed_database()
    yield


app = FastAPI(
    title="CMPUT 401 Assignment 1 API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=400,
        content={
            "status": "error",
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
            },
        },
    )


@app.get("/")
def frontend():
    return FileResponse("frontend/index.html")

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get(
    "/api/v1/items",
    responses={
        400: {
            "description": "Invalid pagination parameters",
        },
    },
)
def list_items(
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
):
    items = get_items(limit, offset)

    return {
        "status": "ok",
        "data": items,
    }


@app.get(
    "/api/v1/items/{item_id}",
    responses={
        404: {
            "description": "Item not found",
        }
    },
)
def get_single_item(item_id: str):
    item = get_item(item_id)

    if item is None:
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Item not found",
                },
            },
        )

    return {
        "status": "ok",
        "data": item,
    }


@app.post(
    "/api/v1/items",
    status_code=201,
    responses={
        400: {
            "description": "Validation error",
        }
    },
)
def create_new_item(item: ItemCreate):
    item_id = str(uuid.uuid4())

    created_item = create_item(
        item_id,
        item.model_dump(),
    )

    return {
        "status": "ok",
        "data": created_item,
    }

@app.patch(
    "/api/v1/items/{item_id}",
    responses={
        400: {
            "description": "Validation error",
        },
        404: {
            "description": "Item not found",
        },
    },
)
def update_existing_item(item_id: str, item: ItemUpdate):
    updates = item.model_dump(exclude_unset=True)

    updated_item = update_item(item_id, updates)

    if updated_item is None:
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Item not found",
                },
            },
        )

    return {
        "status": "ok",
        "data": updated_item,
    }

@app.delete(
    "/api/v1/items/{item_id}",
    status_code=204,
    responses={
        404: {
            "description": "Item not found",
        },
    },
)
def delete_existing_item(item_id: str):
    deleted = delete_item(item_id)

    if not deleted:
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Item not found",
                },
            },
        )

    return Response(status_code=204)