from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class Source(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if not value.strip():
            raise ValueError("Source name must be a non-empty string")
        return value


class ItemCreate(BaseModel):
    model_config = ConfigDict(strict=True)

    title: str
    source: Source
    publishedAt: str
    url: str
    summary: str
    tags: list[str]

    @field_validator("title")
    @classmethod
    def validate_title(cls, value):
        if not value.strip():
            raise ValueError("Title must be a non-empty string")
        return value

    @field_validator("publishedAt")
    @classmethod
    def validate_published_at(cls, value):
        if not value.endswith("Z"):
            raise ValueError("publishedAt must be a UTC datetime ending in Z")

        try:
            datetime.fromisoformat(value[:-1] + "+00:00")
        except ValueError:
            raise ValueError("publishedAt must be a valid UTC datetime")

        return value

    @field_validator("url")
    @classmethod
    def validate_url(cls, value):
        if not value.strip():
            raise ValueError("URL must be a non-empty string")
        return value

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value):
        if not all(isinstance(tag, str) for tag in value):
            raise ValueError("All tags must be strings")
        return value


class ItemUpdate(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
    )

    title: str | None = None
    source: Source | None = None
    publishedAt: str | None = None
    url: str | None = None
    summary: str | None = None
    tags: list[str] | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value):
        if not value.strip():
            raise ValueError("Title must be a non-empty string")
        return value

    @field_validator("publishedAt")
    @classmethod
    def validate_published_at(cls, value):
        if not value.endswith("Z"):
            raise ValueError("publishedAt must be a UTC datetime ending in Z")

        try:
            datetime.fromisoformat(value[:-1] + "+00:00")
        except ValueError:
            raise ValueError("publishedAt must be a valid UTC datetime")

        return value

    @field_validator("url")
    @classmethod
    def validate_url(cls, value):
        if not value.strip():
            raise ValueError("URL must be a non-empty string")
        return value

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value):
        if not all(isinstance(tag, str) for tag in value):
            raise ValueError("All tags must be strings")
        return value


class Item(ItemCreate):
    id: str