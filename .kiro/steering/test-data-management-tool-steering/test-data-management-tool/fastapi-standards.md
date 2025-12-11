---
inclusion: manual
---

# FastAPI Backend Standards

This document defines coding standards and best practices for building the Test Data Management Tool backend using Python and FastAPI.

## Project Structure

```
src/
├── api/
│   └── v1/
│       ├── endpoints/
│       │   ├── datasets.py
│       │   ├── schemas.py
│       │   ├── templates.py
│       │   ├── environments.py
│       │   └── masking.py
│       └── router.py
├── core/
│   ├── config.py
│   ├── database.py
│   ├── security.py
│   └── dependencies.py
├── services/
│   ├── data_generation.py
│   ├── data_masking.py
│   ├── environment_management.py
│   └── version_control.py
├── repositories/
│   ├── dataset_repository.py
│   ├── schema_repository.py
│   └── template_repository.py
├── models/
│   ├── dataset.py
│   ├── schema.py
│   └── template.py
└── utils/
    ├── validators.py
    └── helpers.py
```

## FastAPI Application Setup

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.database import init_db, close_db
from api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()

app = FastAPI(
    title="Test Data Management API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(api_router, prefix="/api/v1")
```

## Endpoint Patterns

```python
# api/v1/endpoints/datasets.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from models.dataset import Dataset, DatasetCreate, DatasetUpdate
from services.data_generation import DataGenerationService
from core.dependencies import get_current_user

router = APIRouter(prefix="/datasets", tags=["datasets"])

@router.post("/", response_model=Dataset, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    dataset: DatasetCreate,
    service: DataGenerationService = Depends(),
    current_user = Depends(get_current_user)
):
    """Generate a new dataset."""
    return await service.generate_dataset(dataset, current_user.id)

@router.get("/{dataset_id}", response_model=Dataset)
async def get_dataset(
    dataset_id: str,
    service: DataGenerationService = Depends()
):
    """Get dataset by ID."""
    dataset = await service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset {dataset_id} not found"
        )
    return dataset
```

## Service Layer Pattern

```python
# services/data_generation.py
from typing import List, Optional
from models.dataset import Dataset, DatasetCreate
from repositories.dataset_repository import DatasetRepository

class DataGenerationService:
    def __init__(self):
        self.repository = DatasetRepository()
        self.generator = DataGenerator()
    
    async def generate_dataset(
        self,
        request: DatasetCreate,
        user_id: str
    ) -> Dataset:
        """Generate a new dataset."""
        # Validate schema
        schema = await self._validate_schema(request.schema_id)
        
        # Generate data
        records = await self.generator.generate(
            schema=schema,
            count=request.record_count
        )
        
        # Create dataset
        dataset = Dataset(
            name=request.name,
            schema_id=request.schema_id,
            records=records,
            created_by=user_id
        )
        
        return await self.repository.create(dataset)
```

## Pydantic Models

```python
# models/dataset.py
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID, uuid4

class DatasetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    schema_id: UUID
    environment: str = Field(default="development")

class DatasetCreate(DatasetBase):
    record_count: int = Field(..., gt=0, le=1000000)
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

class Dataset(DatasetBase):
    id: UUID = Field(default_factory=uuid4)
    version: str = "1.0.0"
    status: str = "active"
    records: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: UUID
    
    class Config:
        from_attributes = True
```

## Database Integration

```python
# core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient

from core.config import settings

# PostgreSQL for metadata
engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# MongoDB for datasets
mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
mongo_db = mongo_client[settings.MONGODB_DATABASE]

async def get_db():
    async with async_session() as session:
        yield session

async def get_mongo_db():
    return mongo_db
```

## Error Handling

```python
# core/exceptions.py
from fastapi import HTTPException, status

class DatasetNotFoundError(HTTPException):
    def __init__(self, dataset_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset {dataset_id} not found"
        )

class SchemaValidationError(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Schema validation failed: {message}"
        )
```

## Testing Standards

```python
# tests/test_datasets.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_create_dataset():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/datasets/",
            json={
                "name": "Test Dataset",
                "schema_id": "123e4567-e89b-12d3-a456-426614174000",
                "record_count": 100
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Dataset"
```
