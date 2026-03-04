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
        self.products_db = {}  # In production, use actual database
        self._initialize_sample_products()
    
    def _initialize_sample_products(self):
        """Initialize sample products for demonstration"""
        self.products_db = {
            'prod_001': {
                'id': 'prod_001',
                'name': 'Premium Laptop',
                'description': 'High-performance laptop with 16GB RAM and 512GB SSD',
                'category': 'Electronics',
                'price': 1299.99,
                'tags': ['laptop', 'computer', 'work', 'professional']
            },
            'prod_002': {
                'id': 'prod_002',
                'name': 'Wireless Mouse',
                'description': 'Ergonomic wireless mouse with 2.4GHz connection',
                'category': 'Accessories',
                'price': 49.99,
                'tags': ['mouse', 'wireless', 'computer', 'accessory']
            },
            'prod_003': {
                'id': 'prod_003',
                'name': 'USB-C Hub',
                'description': 'Multi-port USB-C hub with HDMI and SD card reader',
                'category': 'Accessories',
                'price': 79.99,
                'tags': ['hub', 'usb-c', 'connector', 'accessory']
            },
            'prod_004': {
                'id': 'prod_004',
                'name': 'Mechanical Keyboard',
                'description': 'RGB mechanical keyboard with mechanical switches',
                'category': 'Accessories',
                'price': 149.99,
                'tags': ['keyboard', 'mechanical', 'rgb', 'gaming']
            },
        }
    
    def _keyword_search(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Perform keyword search on products"""
        results = []
        query_lower = query.lower()
        
        for product in self.products_db.values():
            # Check if query matches name or tags
            if (query_lower in product['name'].lower() or 
                query_lower in product['description'].lower() or
                any(query_lower in tag for tag in product.get('tags', []))):
                
                # Apply filters if provided
                if filters:
                    if filters.get('category') and product['category'] != filters['category']:
                        continue
                    if filters.get('min_price') and product['price'] < filters['min_price']:
                        continue
                    if filters.get('max_price') and product['price'] > filters['max_price']:
                        continue
                
                results.append(product)
        
        return results
    
    def _vector_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Perform vector/semantic search on products"""
        try:
            # Generate embedding for query
            query_embedding = embedding_service.get_embedding(query)
            
            results = []
            for product in self.products_db.values():
                # Generate embedding for product
                product_text = f"{product['name']} {product['description']}"
                product_embedding = embedding_service.get_embedding(product_text)
                
                # Calculate similarity
                similarity = embedding_service.similarity(query_embedding, product_embedding)
                
                if similarity > 0.3:  # Threshold
                    product_with_score = product.copy()
                    product_with_score['relevance_score'] = similarity
                    results.append(product_with_score)
            
            # Sort by relevance
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            return results[:limit]
        
        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            return []
    
    def search(self, request: SearchRequest) -> SearchResult:
        """
        Perform search using specified search type
        
        Args:
            request: Search request with query and filters
            
        Returns:
            Search results
        """
        start_time = time.time()
        
        if request.search_type == "keyword":
            items = self._keyword_search(request.query, request.filters)
        elif request.search_type == "vector":
            items = self._vector_search(request.query, request.limit)
        else:  # hybrid
            keyword_results = self._keyword_search(request.query, request.filters)
            vector_results = self._vector_search(request.query, request.limit * 2)
            
            # Combine and deduplicate
            combined = {}
            for item in keyword_results:
                combined[item['id']] = item
            for item in vector_results:
                if item['id'] not in combined:
                    combined[item['id']] = item
            
            items = list(combined.values())[:request.limit]
        
        # Apply limit
        items = items[:request.limit]
        
        search_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return SearchResult(
            items=items,
            total_count=len(items),
            search_time_ms=search_time
        )


search_service = SearchService()
