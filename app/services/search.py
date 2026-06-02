"""
Search Service with keyword and vector search capabilities
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models import SearchRequest, SearchResult
from app.utils import embedding_service
import time

logger = logging.getLogger(__name__)


class SearchService:
    """Service for hybrid search (keyword + vector search)"""

    def __init__(self):
        self._initialize_sample_products()

    def _initialize_sample_products(self):
        """Keep sample products for bootstrap when DB not seeded."""
        from app.db import SessionLocal
        from app.repositories.product_repository import product_repository

        sample_products = [
            {
                'id': 'prod_001',
                'name': 'Premium Laptop',
                'description': 'High-performance laptop with 16GB RAM and 512GB SSD',
                'category': 'Electronics',
                'price': 1299.99,
                'tags': ['laptop', 'computer', 'work', 'professional'],
                'inventory': 30,
            },
            {
                'id': 'prod_002',
                'name': 'Wireless Mouse',
                'description': 'Ergonomic wireless mouse with 2.4GHz connection',
                'category': 'Accessories',
                'price': 49.99,
                'tags': ['mouse', 'wireless', 'computer', 'accessory'],
                'inventory': 120,
            },
            {
                'id': 'prod_003',
                'name': 'USB-C Hub',
                'description': 'Multi-port USB-C hub with HDMI and SD card reader',
                'category': 'Accessories',
                'price': 79.99,
                'tags': ['hub', 'usb-c', 'connector', 'accessory'],
                'inventory': 70,
            },
            {
                'id': 'prod_004',
                'name': 'Mechanical Keyboard',
                'description': 'RGB mechanical keyboard with mechanical switches',
                'category': 'Accessories',
                'price': 149.99,
                'tags': ['keyboard', 'mechanical', 'rgb', 'gaming'],
                'inventory': 50,
            },
        ]

        with SessionLocal() as db:
            for product in sample_products:
                product_repository.create_or_update(db, product)

    def _keyword_search(self, request: SearchRequest) -> List[dict]:
        from app.db import SessionLocal
        from app.repositories.product_repository import product_repository

        with SessionLocal() as db:
            results = product_repository.search(db, request.query or "", request.filters or {}, request.limit)
            return [product.__dict__ for product in results]

    def _vector_search(self, request: SearchRequest) -> List[dict]:
        from app.db import SessionLocal
        from app.repositories.product_repository import product_repository

        try:
            with SessionLocal() as db:
                results = product_repository.search(db, request.query or "", request.filters or {}, request.limit * 2)

            query_embedding = embedding_service.get_embedding(request.query)
            scored_results = []
            for item in results:
                product_text = f"{item.name} {item.description}"
                similarity = embedding_service.similarity(query_embedding, embedding_service.get_embedding(product_text))
                if similarity > 0.25:
                    row = item.__dict__.copy()
                    row['relevance_score'] = similarity
                    scored_results.append(row)
            scored_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            return scored_results[:request.limit]

        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            return []

    def search(self, request: SearchRequest) -> SearchResult:
        start_time = time.time()

        if request.search_type == "keyword":
            items = self._keyword_search(request)
        elif request.search_type == "vector":
            items = self._vector_search(request)
        else:
            keyword_results = self._keyword_search(request)
            vector_results = self._vector_search(request)
            combined = {item['id']: item for item in keyword_results}
            for item in vector_results:
                if item['id'] not in combined:
                    combined[item['id']] = item
            items = list(combined.values())[:request.limit]

        duration_ms = (time.time() - start_time) * 1000
        return SearchResult(items=items, total_count=len(items), search_time_ms=duration_ms)


search_service = SearchService()
