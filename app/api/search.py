"""
Search API endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
import logging
from app.models import SearchRequest, SearchResult
from app.services import search_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.get("/products", response_model=SearchResult)
async def search_products(
    q: str = Query(..., min_length=1, description="Search query"),
    search_type: str = Query(default="hybrid", description="Search type: keyword, vector, hybrid"),
    limit: int = Query(default=10, le=100, ge=1),
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    """
    Search for products
    
    Args:
        q: Search query
        search_type: Type of search (keyword, vector, hybrid)
        limit: Maximum results
        category: Filter by category
        min_price: Minimum price filter
        max_price: Maximum price filter
        
    Returns:
        Search results
    """
    try:
        filters = {}
        if category:
            filters['category'] = category
        if min_price is not None:
            filters['min_price'] = min_price
        if max_price is not None:
            filters['max_price'] = max_price
        
        request = SearchRequest(
            query=q,
            filters=filters if filters else None,
            search_type=search_type,
            limit=limit
        )
        
        result = search_service.search(request)
        return result
    
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/advanced", response_model=SearchResult)
async def advanced_search(request: SearchRequest):
    """
    Advanced search with full request body
    
    Args:
        request: Search request
        
    Returns:
        Search results
    """
    try:
        result = search_service.search(request)
        return result
    
    except Exception as e:
        logger.error(f"Error in advanced search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending")
async def get_trending_products(
    limit: int = Query(default=10, le=50, ge=1)
):
    """
    Get trending products
    
    Args:
        limit: Number of products
        
    Returns:
        Trending products
    """
    try:
        # In production, fetch actual trending products
        trending = search_service._initialize_sample_products()
        products = list(trending.values())[:limit]
        
        return {
            "items": products,
            "total_count": len(products),
            "search_time_ms": 5.0
        }
    
    except Exception as e:
        logger.error(f"Error getting trending products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/{category}")
async def search_by_recommendations(
    category: str,
    limit: int = Query(default=5, le=20, ge=1)
):
    """
    Get recommended products for a category
    
    Args:
        category: Product category
        limit: Number of results
        
    Returns:
        Recommended products
    """
    try:
        request = SearchRequest(
            query=category,
            search_type="vector",
            limit=limit
        )
        result = search_service.search(request)
        return result
    
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
