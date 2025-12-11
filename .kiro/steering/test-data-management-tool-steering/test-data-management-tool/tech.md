---
inclusion: manual
---

# Test Data Management Tool - Technology Stack

This document defines the comprehensive technology stack for the Test Data Management Tool, focusing on Python FastAPI backend, React TypeScript frontend, and cloud-native deployment.

## Core Technology Stack

### Backend Services

**Primary Language**: Python 3.11+
**Web Framework**: FastAPI
**Async Runtime**: asyncio with uvicorn
**Data Processing**: Pandas, NumPy
**Data Generation**: Faker, Mimesis
**Testing**: pytest, pytest-asyncio

### Frontend Application

**Framework**: React 18 with TypeScript
**Build Tool**: Vite
**UI Library**: Material-UI (MUI)
**State Management**: Redux Toolkit + RTK Query
**HTTP Client**: Axios
**Testing**: Jest, React Testing Library

### Database Layer

**Metadata Database**: PostgreSQL 15+
**Document Storage**: MongoDB 6.0+
**Caching**: Redis 7.0+
**Search Engine**: Elasticsearch 8.0+
**Message Queue**: RabbitMQ / Redis Streams

### Cloud Infrastructure

**Container Platform**: Docker + Kubernetes
**Cloud Provider**: AWS / Azure / GCP
**API Gateway**: Kong / AWS API Gateway
**Monitoring**: Prometheus + Grafana
**Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)

## Backend Architecture

### FastAPI Application Structure

```python
# main.py - Application entry point
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import uvicorn

from core.config import settings
from core.database import init_db, close_db
from api.v1.router import api_router
from middleware.auth import AuthMiddleware
from middleware.logging import LoggingMiddleware
from middleware.rate_limiting import RateLimitMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()

app = FastAPI(
    title="Test Data Management API",
    description="Comprehensive test data generation and management platform",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# Routes
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
```

### Project Structure

```
test-data-management-tool/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   └── exceptions.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── router.py
│   │   │       ├── endpoints/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── datasets.py
│   │   │       │   ├── schemas.py
│   │   │       │   ├── templates.py
│   │   │       │   ├── environments.py
│   │   │       │   └── masking.py
│   │   │       └── dependencies.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── data_generation.py
│   │   │   ├── data_masking.py
│   │   │   ├── environment_management.py
│   │   │   ├── version_control.py
│   │   │   └── integration.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── dataset.py
│   │   │   ├── schema.py
│   │   │   ├── template.py
│   │   │   ├── environment.py
│   │   │   └── user.py
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── dataset_repository.py
│   │   │   ├── schema_repository.py
│   │   │   └── template_repository.py
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── logging.py
│   │   │   └── rate_limiting.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── data_generators.py
│   │       ├── validators.py
│   │       └── helpers.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── Dockerfile
│   └── docker-compose.yml
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── store/
│   │   ├── services/
│   │   ├── types/
│   │   └── utils/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── Dockerfile
└── deployment/
    ├── kubernetes/
    ├── docker/
    └── scripts/
```

## Backend Technology Details

### FastAPI Configuration

```python
# core/config.py
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Test Data Management Tool"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str
    MONGODB_URL: str
    REDIS_URL: str
    ELASTICSEARCH_URL: str
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Data Generation
    MAX_RECORDS_PER_REQUEST: int = 1000000
    DEFAULT_BATCH_SIZE: int = 10000
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### Database Configuration

```python
# core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
from elasticsearch import AsyncElasticsearch

from core.config import settings

# PostgreSQL (Metadata)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

# MongoDB (Datasets)
mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
mongodb_db = mongodb_client.testdata

# Redis (Caching)
redis_client = redis.from_url(settings.REDIS_URL)

# Elasticsearch (Search)
elasticsearch_client = AsyncElasticsearch([settings.ELASTICSEARCH_URL])

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db():
    await engine.dispose()
    mongodb_client.close()
    await redis_client.close()
    await elasticsearch_client.close()
```

### Data Models

```python
# models/dataset.py
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from core.database import Base

class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    schema_id = Column(UUID(as_uuid=True), ForeignKey("schemas.id"), nullable=False)
    environment_id = Column(UUID(as_uuid=True), ForeignKey("environments.id"), nullable=False)
    version = Column(String(50), nullable=False, default="1.0.0")
    status = Column(String(50), nullable=False, default="active")
    record_count = Column(Integer, default=0)
    size_bytes = Column(Integer, default=0)
    metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    schema = relationship("Schema", back_populates="datasets")
    environment = relationship("Environment", back_populates="datasets")
    creator = relationship("User", back_populates="datasets")
    versions = relationship("DatasetVersion", back_populates="dataset")
```

### Service Layer

```python
# services/data_generation.py
from typing import List, Dict, Any, Optional
import asyncio
from faker import Faker
import pandas as pd

from models.dataset import Dataset
from models.schema import Schema
from repositories.dataset_repository import DatasetRepository
from utils.data_generators import DataGeneratorFactory

class DataGenerationService:
    def __init__(self, dataset_repo: DatasetRepository):
        self.dataset_repo = dataset_repo
        self.faker = Faker()
        self.generator_factory = DataGeneratorFactory()
    
    async def generate_dataset(
        self,
        schema_id: str,
        record_count: int,
        environment_id: str,
        user_id: str,
        **kwargs
    ) -> Dataset:
        """Generate a new dataset based on schema definition."""
        # Validate schema
        schema = await self.dataset_repo.get_schema(schema_id)
        if not schema:
            raise ValueError(f"Schema {schema_id} not found")
        
        # Create dataset record
        dataset = Dataset(
            name=kwargs.get('name', f"Generated Dataset {schema.name}"),
            description=kwargs.get('description'),
            schema_id=schema_id,
            environment_id=environment_id,
            created_by=user_id,
            record_count=record_count
        )
        
        # Generate data in batches
        batch_size = kwargs.get('batch_size', 10000)
        records = []
        
        for batch_start in range(0, record_count, batch_size):
            batch_end = min(batch_start + batch_size, record_count)
            batch_records = await self._generate_batch(
                schema, batch_end - batch_start
            )
            records.extend(batch_records)
        
        # Save dataset
        dataset = await self.dataset_repo.create_dataset(dataset, records)
        return dataset
    
    async def _generate_batch(self, schema: Schema, count: int) -> List[Dict[str, Any]]:
        """Generate a batch of records based on schema."""
        records = []
        for _ in range(count):
            record = {}
            for field in schema.fields:
                generator = self.generator_factory.get_generator(field.type)
                record[field.name] = await generator.generate(field.config)
            records.append(record)
        return records
```

## Frontend Technology Stack

### React TypeScript Setup

```typescript
// src/main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'

import App from './App'
import { store } from './store'
import { theme } from './theme'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Provider store={store}>
      <BrowserRouter>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <App />
        </ThemeProvider>
      </BrowserRouter>
    </Provider>
  </React.StrictMode>,
)
```

### Redux Store Configuration

```typescript
// src/store/index.ts
import { configureStore } from '@reduxjs/toolkit'
import { setupListeners } from '@reduxjs/toolkit/query'
import { apiSlice } from './api/apiSlice'
import authReducer from './slices/authSlice'
import datasetReducer from './slices/datasetSlice'
import schemaReducer from './slices/schemaSlice'

export const store = configureStore({
  reducer: {
    api: apiSlice.reducer,
    auth: authReducer,
    datasets: datasetReducer,
    schemas: schemaReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(apiSlice.middleware),
})

setupListeners(store.dispatch)

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
```

### API Service Layer

```typescript
// src/services/api.ts
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import type { RootState } from '../store'

const baseQuery = fetchBaseQuery({
  baseUrl: '/api/v1',
  prepareHeaders: (headers, { getState }) => {
    const token = (getState() as RootState).auth.token
    if (token) {
      headers.set('authorization', `Bearer ${token}`)
    }
    return headers
  },
})

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery,
  tagTypes: ['Dataset', 'Schema', 'Template', 'Environment'],
  endpoints: (builder) => ({
    // Dataset endpoints
    getDatasets: builder.query<Dataset[], void>({
      query: () => '/datasets',
      providesTags: ['Dataset'],
    }),
    createDataset: builder.mutation<Dataset, CreateDatasetRequest>({
      query: (data) => ({
        url: '/datasets',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Dataset'],
    }),
    generateDataset: builder.mutation<Dataset, GenerateDatasetRequest>({
      query: (data) => ({
        url: '/datasets/generate',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Dataset'],
    }),
    // Schema endpoints
    getSchemas: builder.query<Schema[], void>({
      query: () => '/schemas',
      providesTags: ['Schema'],
    }),
    createSchema: builder.mutation<Schema, CreateSchemaRequest>({
      query: (data) => ({
        url: '/schemas',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Schema'],
    }),
  }),
})

export const {
  useGetDatasetsQuery,
  useCreateDatasetMutation,
  useGenerateDatasetMutation,
  useGetSchemasQuery,
  useCreateSchemaMutation,
} = apiSlice
```

## Development Tools

### Package Configuration

```txt
# backend/requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
motor==3.3.2
redis[hiredis]==5.0.1
elasticsearch[async]==8.11.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
faker==20.1.0
pandas==2.1.4
numpy==1.25.2
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
```

```json
// frontend/package.json
{
  "name": "test-data-management-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "jest",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.1",
    "@reduxjs/toolkit": "^1.9.7",
    "react-redux": "^8.1.3",
    "@mui/material": "^5.14.20",
    "@mui/icons-material": "^5.14.19",
    "@emotion/react": "^11.11.1",
    "@emotion/styled": "^11.11.0",
    "axios": "^1.6.2",
    "date-fns": "^2.30.0",
    "react-hook-form": "^7.48.2",
    "react-query": "^3.39.3"
  },
  "devDependencies": {
    "@types/react": "^18.2.37",
    "@types/react-dom": "^18.2.15",
    "@typescript-eslint/eslint-plugin": "^6.10.0",
    "@typescript-eslint/parser": "^6.10.0",
    "@vitejs/plugin-react": "^4.1.1",
    "eslint": "^8.53.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.4",
    "typescript": "^5.2.2",
    "vite": "^5.0.0",
    "jest": "^29.7.0",
    "@testing-library/react": "^13.4.0",
    "@testing-library/jest-dom": "^6.1.5"
  }
}
```

This technology stack provides a robust, scalable foundation for the Test Data Management Tool with modern development practices, comprehensive testing, and production-ready deployment capabilities.
