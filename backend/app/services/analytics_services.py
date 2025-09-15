from app.db.elastic import get_es_client
import logging
from typing import List, Dict, Any
from datetime import datetime
import asyncio
from app.db.postgresql import AsyncSessionLocal
from app.services.elastic_sync import ElasticSyncService

logger = logging.getLogger(__name__)
SALES_INDEX_NAME = "sales_analytics"
CATEGORIES_INDEX_NAME = "categories_analytics"
CUSTOMERS_INDEX_NAME = "customers_analytics"
CUSTOMERS_AGE_GROUP_INDEX_NAME = "customers_age_group_analytics"


class AnalyticsService:
    def __init__(self):
        self.es = get_es_client()
        self.elastic_sync = ElasticSyncService(self.es, AsyncSessionLocal)

        self.index_mappings = {
            SALES_INDEX_NAME: {
                "mappings": {
                    "properties": {
                        "month": {"type": "date", "format": "yyyy-MM-dd"},
                        "total_sales": {"type": "double"},
                        "transactions_count": {"type": "integer"},
                    }
                },
                "settings": {"number_of_shards": 1, "number_of_replicas": 0},
            },
            CATEGORIES_INDEX_NAME: {
                "mappings": {
                    "properties": {
                        "category": {"type": "keyword"},
                        "sales": {"type": "double"},
                        "percentage": {"type": "double"},
                    }
                },
                "settings": {"number_of_shards": 1, "number_of_replicas": 0},
            },
            CUSTOMERS_INDEX_NAME: {
                "mappings": {
                    "properties": {
                        "category": {"type": "keyword"},
                        "gender": {"type": "keyword"},
                        "customers": {"type": "integer"},
                        "total_items": {"type": "integer"},
                    }
                },
                "settings": {"number_of_shards": 1, "number_of_replicas": 0},
            },
            CUSTOMERS_AGE_GROUP_INDEX_NAME: {
                "mappings": {
                    "properties": {
                        "ageGroup": {"type": "keyword"},
                        "customers": {"type": "integer"},
                        "sales": {"type": "double"},
                    }
                },
                "settings": {"number_of_shards": 1, "number_of_replicas": 0},
            },
        }

    async def ensure_all_indices_exist(self) -> None:
        for index_name, mapping in self.index_mappings.items():
            await self.elastic_sync.ensure_index(index_name, mapping)

    async def sync_sales_analytics(self):
        query = """
            SELECT DATE_TRUNC('month', t.transaction_date)::date AS month, 
                   SUM(t.total_amount) AS total_sales, 
                   COUNT(t.id) AS transactions_count 
            FROM transactions t 
            GROUP BY month
            ORDER BY month;
        """
        def transform(row):
            source = {
                "month": row.month.strftime("%Y-%m-%d"),
                "total_sales": float(row.total_sales),
                "transactions_count": int(row.transactions_count),
            }
            return source, row.month.strftime("%Y-%m-%d")

        return await self.elastic_sync.sync_to_es(SALES_INDEX_NAME, query, transform)

    async def sync_categories_analytics(self):
        query = """
            WITH monthly_sales_by_category AS (
                SELECT
                    DATE_TRUNC('month', t.transaction_date) AS bulan,
                    pc.name AS category,
                    SUM(ti.subtotal) AS total_sales
                FROM transaction_items ti
                JOIN products p ON p.id = ti.product_id
                JOIN product_categories pc ON pc.id = p.category_id
                JOIN transactions t ON t.id = ti.transaction_id
                WHERE DATE_TRUNC('month', t.transaction_date) = DATE_TRUNC('month', CURRENT_DATE)
                GROUP BY bulan, category
            )
            SELECT
                bulan,
                category,
                total_sales,
                ROUND((total_sales / SUM(total_sales) OVER (PARTITION BY bulan)) * 100, 2) AS percentage
            FROM monthly_sales_by_category
            ORDER BY total_sales DESC;
        """
        def transform(row):
            source = {
                "category": row.category,
                "sales": float(row.total_sales),
                "percentage": float(row.percentage),
            }
            return source, f"{row.bulan.strftime('%Y-%m')}-{row.category}"

        return await self.elastic_sync.sync_to_es(CATEGORIES_INDEX_NAME, query, transform)

    async def sync_customers_analytics(self):
        query = """
            SELECT 
                pc.name AS category,
                c.gender,
                COUNT(DISTINCT c.id) AS customers,
                SUM(ti.quantity) AS total_items
            FROM customers c
            JOIN transactions t ON t.customer_id = c.id
            JOIN transaction_items ti ON ti.transaction_id = t.id
            JOIN products p ON p.id = ti.product_id
            JOIN product_categories pc ON pc.id = p.category_id
            GROUP BY pc.name, c.gender
            ORDER BY pc.name, c.gender;
        """
        def transform(row):
            source = {
                "category": row.category,
                "gender": row.gender,
                "customers": int(row.customers),
                "total_items": int(row.total_items),
            }
            return source, f"{row.category}-{row.gender}"

        return await self.elastic_sync.sync_to_es(CUSTOMERS_INDEX_NAME, query, transform)

    async def sync_customers_age_group_analytics(self):
        query = """
            SELECT 
                CASE
                    WHEN c.age BETWEEN 18 AND 24 THEN '18-24'
                    WHEN c.age BETWEEN 25 AND 34 THEN '25-34'
                    WHEN c.age BETWEEN 35 AND 44 THEN '35-44'
                    WHEN c.age BETWEEN 45 AND 55 THEN '45-55'
                    ELSE '55++'
                END AS age_group,
                COUNT(DISTINCT c.id) AS customers,
                SUM(t.total_amount) AS sales
            FROM customers c
            JOIN transactions t ON t.customer_id = c.id
            GROUP BY age_group
            ORDER BY age_group;
        """
        def transform(row):
            source = {
                "ageGroup": row.age_group,
                "customers": int(row.customers),
                "sales": float(row.sales),
            }
            return source, f"{row.age_group}"

        return await self.elastic_sync.sync_to_es(CUSTOMERS_AGE_GROUP_INDEX_NAME, query, transform)


async def get_sales_from_es() -> List[Dict[str, Any]]:
    """Retrieve sales analytics data from Elasticsearch"""
    try:
        es = get_es_client()
        
        if not es.ping():
            raise ConnectionError("Cannot connect to Elasticsearch")
        
        if not es.indices.exists(index=SALES_INDEX_NAME):
            logger.warning(f"Index {SALES_INDEX_NAME} does not exist")
            return []

        query_body = {
            "size": 1000,
            "sort": [{"month": {"order": "asc"}}],
            "query": {"match_all": {}},
            "_source": ["month", "total_sales", "transactions_count"]
        }

        resp = await asyncio.to_thread(es.search, index=SALES_INDEX_NAME, body=query_body)
        
        data = []
        for hit in resp["hits"]["hits"]:
            source = hit["_source"]
            data.append({
                "month": datetime.fromisoformat(source["month"]).strftime("%b %Y"),
                "total_sales": source["total_sales"],
                "transactions_count": source["transactions_count"],
            })
        
        logger.info(f"Retrieved {len(data)} records from Elasticsearch")
        return data

    except Exception as e:
        logger.error(f"Error in get_sales_from_es: {str(e)}")
        raise


async def get_categories_from_es() -> List[Dict[str, Any]]:
    """Retrieve categories analytics data from Elasticsearch"""
    try:
        es = get_es_client()
        
        if not es.ping():
            raise ConnectionError("Cannot connect to Elasticsearch")
        
        if not es.indices.exists(index=CATEGORIES_INDEX_NAME):
            logger.warning(f"Index {CATEGORIES_INDEX_NAME} does not exist")
            return []

        query_body = {
            "size": 1000,
            "query": {"match_all": {}},
            "_source": ["category", "sales", "percentage"]
        }

        resp = await asyncio.to_thread(es.search, index=CATEGORIES_INDEX_NAME, body=query_body)
        
        data = []
        for hit in resp["hits"]["hits"]:
            source = hit["_source"]
            data.append({
                "category": source["category"],
                "sales": source["sales"],
                "percentage": source["percentage"],
            })
        
        logger.info(f"Retrieved {len(data)} records from Elasticsearch")
        return data

    except Exception as e:
        logger.error(f"Error in get_sales_from_es: {str(e)}")
        raise
    
async def get_customers_from_es() -> List[Dict[str, Any]]:
    """Retrieve categories analytics data from Elasticsearch"""
    try:
        es = get_es_client()
        
        if not es.ping():
            raise ConnectionError("Cannot connect to Elasticsearch")
        
        if not es.indices.exists(index=CUSTOMERS_INDEX_NAME):
            logger.warning(f"Index {CUSTOMERS_INDEX_NAME} does not exist")
            return []

        query_body = {
            "size": 1000,
            "query": {"match_all": {}},
            "_source": ["category", "gender", "customers", "total_items"]
        }

        resp = await asyncio.to_thread(es.search, index=CUSTOMERS_INDEX_NAME, body=query_body)
        
        print(resp)
        
        data = []
        for hit in resp["hits"]["hits"]:
            source = hit["_source"]
            data.append({
                "category": source["category"],
                "gender": source["gender"],
                "customers": source["customers"],
                "total_items": source["total_items"],
            })
        
        logger.info(f"Retrieved {len(data)} records from Elasticsearch")
        return data

    except Exception as e:
        logger.error(f"Error in get_sales_from_es: {str(e)}")
        raise
    
async def get_customers_age_group_from_es() -> List[Dict[str, Any]]:
    """Retrieve categories analytics data from Elasticsearch"""
    try:
        es = get_es_client()
        
        if not es.ping():
            raise ConnectionError("Cannot connect to Elasticsearch")
        
        if not es.indices.exists(index=CUSTOMERS_AGE_GROUP_INDEX_NAME):
            logger.warning(f"Index {CUSTOMERS_AGE_GROUP_INDEX_NAME} does not exist")
            return []  
        
        query_body = {
            "size": 1000,
            "query": {"match_all": {}},
            "_source": ["ageGroup", "customers", "sales"]
        }
        
        resp = await asyncio.to_thread(es.search, index=CUSTOMERS_AGE_GROUP_INDEX_NAME, body=query_body) 
        
        data = []
        for hit in resp["hits"]["hits"]:
            source = hit["_source"]
            data.append({
                "age_group": source["ageGroup"],
                "customers": source["customers"],
                "sales": source["sales"]
            })
        
        logger.info(f"Retrieved {len(data)} records from Elasticsearch")
        return data
    
    except Exception as e:
        logger.error(f"Error in get_sales_from_es: {str(e)}")
        raise  
        
                
            