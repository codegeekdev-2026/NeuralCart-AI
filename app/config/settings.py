"""
Configuration settings for E-commerce Personalization Platform
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_TITLE: str = "AI E-commerce Personalization Platform"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-4"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Vector Database Configuration
    VECTOR_DB_TYPE: str = Field(default="faiss", env="VECTOR_DB_TYPE")  # faiss or pinecone
    PINECONE_API_KEY: Optional[str] = Field(default=None, env="PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: Optional[str] = Field(default=None, env="PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME: str = "ecommerce-products"
    FAISS_INDEX_PATH: str = "./data/faiss_index.pkl"
    
    # ElasticSearch Configuration
    ELASTICSEARCH_HOST: str = Field(default="localhost:9200", env="ELASTICSEARCH_HOST")
    ELASTICSEARCH_USERNAME: Optional[str] = Field(default=None, env="ELASTICSEARCH_USERNAME")
    ELASTICSEARCH_PASSWORD: Optional[str] = Field(default=None, env="ELASTICSEARCH_PASSWORD")
    
    # Payment API Configuration
    STRIPE_API_KEY: str = Field(default="", env="STRIPE_API_KEY")
    STRIPE_SECRET_KEY: str = Field(default="", env="STRIPE_SECRET_KEY")
    PAYMENT_WEBHOOK_SECRET: str = Field(default="", env="PAYMENT_WEBHOOK_SECRET")
    
    # Cart API Configuration
    CART_API_BASE_URL: str = Field(default="http://localhost:8001", env="CART_API_BASE_URL")
    
    # AWS Configuration
    AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
    AWS_ACCESS_KEY_ID: str = Field(default="", env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = Field(default="", env="AWS_SECRET_ACCESS_KEY")
    S3_BUCKET: str = Field(default="ecommerce-personalization", env="S3_BUCKET")
    
    # Cache Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    CACHE_TTL: int = 3600  # 1 hour
    
    # Database Configuration
    DATABASE_URL: str = Field(default="postgresql://user:password@localhost/ecommerce", env="DATABASE_URL")
    
    # Agent Configuration
    AGENT_TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2000
    
    # Recommendation Configuration
    MIN_RECOMMENDATION_CONFIDENCE: float = 0.5
    MAX_RECOMMENDATIONS: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
