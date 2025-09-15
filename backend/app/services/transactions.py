from sqlalchemy import select, desc, text, func
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.models.transactions import PaginatedTransactionItems, TransactionItemModel, PaginationMetaData
from app.models.global_type import PaginationMetaData
from app.db.elastic import get_es_client
from app.db.postgresql import AsyncSessionLocal
from app.db.schemas import Transaction, TransactionItem
from app.services.elastic_sync import ElasticSyncService
import asyncio
import logging
import math
from elasticsearch import AsyncElasticsearch, Elasticsearch
from datetime import datetime
from app.utils.utils import format_datetime_for_es
import json

logger = logging.getLogger(__name__)
TRANSACTIONS_INDEX_NAME = "transactions"
TRANSACTIONS_ITEMS_INDEX_NAME = "transaction_items"
CUSTOMERS_INDEX_NAME = "customers"
PRODUCTS_INDEX_NAME = "products"


class TransactionsServices:
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100
    
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._es_client: Optional[AsyncElasticsearch] = None 
    
    async def get_es_client(self) -> AsyncElasticsearch:
        if self._es_client is None:
            self._es_client = AsyncElasticsearch(
                hosts=[{
                    "scheme": "http",
                    "host": "localhost",
                    "port": 9200
                }],
                request_timeout=30,
                max_retries=3,
                retry_on_timeout=True,
            )
        return self._es_client
    
    async def close_connections(self):
        if self._es_client:
            await self._es_client.close()
            self._es_client = None
    
    async def debug_indices(self):
        """Debug method to check if indices exist and have data"""
        es_client = await self.get_es_client()
        
        indices_to_check = [
            TRANSACTIONS_INDEX_NAME,
            TRANSACTIONS_ITEMS_INDEX_NAME,
            CUSTOMERS_INDEX_NAME,
            PRODUCTS_INDEX_NAME
        ]
        
        debug_info = {}
        
        for index_name in indices_to_check:
            try:
                exists = await es_client.indices.exists(index=index_name)
                if not exists:
                    debug_info[index_name] = {"exists": False, "count": 0}
                    continue
                
                count_response = await es_client.count(index=index_name)
                count = count_response.get('count', 0)
                
                sample_query = {"size": 1}
                sample_response = await es_client.search(index=index_name, body=sample_query)
                sample_doc = None
                if sample_response['hits']['hits']:
                    sample_doc = sample_response['hits']['hits'][0]['_source']
                
                debug_info[index_name] = {
                    "exists": True,
                    "count": count,
                    "sample_doc": sample_doc
                }
                
            except Exception as e:
                debug_info[index_name] = {"error": str(e)}
        
        logger.info(f"Elasticsearch indices debug info: {json.dumps(debug_info, indent=2, default=str)}")
        return debug_info
    
    async def get_transactions_data_with_debug(
        self, 
        page: int = 1, 
        page_size: int = DEFAULT_PAGE_SIZE, 
        query_string: Optional[str] = None
    ):
        """Enhanced version with detailed logging for debugging"""
        
        es_client = await self.get_es_client()
        
        debug_info = await self.debug_indices()
        
        from_ = (page - 1) * page_size
        
        logger.info(f"Fetching transactions with page={page}, page_size={page_size}, from_={from_}")
        
        transaction_query = {
            "from": from_,
            "size": page_size,
            "_source": ["id", "transaction_date", "customer_id", "total_amount"],
            "sort": [
                {"transaction_date": {"order": "desc"}}
            ]
        }
        
        try:
            transactions_result = await es_client.search(index=TRANSACTIONS_INDEX_NAME, body=transaction_query)
            logger.info(f"Transactions query result: found {transactions_result['hits']['total']['value']} total transactions")
            logger.info(f"Retrieved {len(transactions_result['hits']['hits'])} transactions for current page")
            
            if not transactions_result["hits"]["hits"]:
                logger.warning("No transactions found")
                return []
            
            sample_transaction = transactions_result["hits"]["hits"][0]["_source"]
            logger.info(f"Sample transaction: {json.dumps(sample_transaction, default=str)}")
            
        except Exception as e:
            logger.error(f"Error querying transactions: {e}")
            return []
        
        customer_ids = list(set([t["_source"]["customer_id"] for t in transactions_result["hits"]["hits"]]))
        logger.info(f"Found {len(customer_ids)} unique customer IDs: {customer_ids[:5]}...")  # Show first 5
        
        customers_query = {
            "size": len(customer_ids),
            "query": {
                "terms": {
                    "id": customer_ids
                }
            },
            "_source": ["id", "first_name", "last_name", "gender", "age"],
        }
        
        try:
            customers_result = await es_client.search(index=CUSTOMERS_INDEX_NAME, body=customers_query)
            logger.info(f"Found {len(customers_result['hits']['hits'])} customers")
            
            if customers_result['hits']['hits']:
                sample_customer = customers_result['hits']['hits'][0]['_source']
                logger.info(f"Sample customer: {json.dumps(sample_customer, default=str)}")
            
        except Exception as e:
            logger.error(f"Error querying customers: {e}")
            customers_result = {"hits": {"hits": []}}
        
        customers_lookup = {
            c["_source"]["id"]: c["_source"] for c in customers_result["hits"]["hits"]
        }
        
        transactions_ids = [t["_source"]["id"] for t in transactions_result["hits"]["hits"]]
        logger.info(f"Looking for items for {len(transactions_ids)} transactions")
        
        items_query = {
            "size": 10000,
            "query": {
                "terms": {
                    "transaction_id": transactions_ids
                }
            },
            "_source": ["transaction_id", "product_id", "subtotal"]
        }
        
        try:
            items_result = await es_client.search(index=TRANSACTIONS_ITEMS_INDEX_NAME, body=items_query)
            logger.info(f"Found {len(items_result['hits']['hits'])} transaction items")
            
            if items_result['hits']['hits']:
                sample_item = items_result['hits']['hits'][0]['_source']
                logger.info(f"Sample transaction item: {json.dumps(sample_item, default=str)}")
            
        except Exception as e:
            logger.error(f"Error querying transaction items: {e}")
            items_result = {"hits": {"hits": []}}
        
        product_ids = list(set([item["_source"]["product_id"] for item in items_result["hits"]["hits"]]))
        logger.info(f"Found {len(product_ids)} unique product IDs")
        
        if not product_ids:
            logger.warning("No product IDs found")
        
        products_query = {
            "size": len(product_ids) if product_ids else 0,
            "query": {
                "terms": {
                    "id": product_ids
                }
            },
            "_source": ["id", "name"]
        }
        
        try:
            if product_ids:
                products_result = await es_client.search(index=PRODUCTS_INDEX_NAME, body=products_query)
                logger.info(f"Found {len(products_result['hits']['hits'])} products")
            else:
                products_result = {"hits": {"hits": []}}
        except Exception as e:
            logger.error(f"Error querying products: {e}")
            products_result = {"hits": {"hits": []}}
        
        products_lookup = {
            p["_source"]["id"]: p["_source"]["name"] 
            for p in products_result["hits"]["hits"]
        }
        
        result: list[TransactionItemModel] = []
        for transaction in transactions_result["hits"]["hits"]:
            trans_data = transaction["_source"]
            customer = customers_lookup.get(trans_data["customer_id"], {})
            
            logger.info(f"Processing transaction {trans_data['id']}, customer: {customer}")
            
            trans_items = [
                item["_source"] for item in items_result["hits"]["hits"] 
                if item["_source"]["transaction_id"] == trans_data["id"]
            ]
            
            logger.info(f"Transaction {trans_data['id']} has {len(trans_items)} items")
            
            product_names = []
            total_subtotal = 0
            
            for item in trans_items:
                product_name = products_lookup.get(item["product_id"], "Unknown")
                product_names.append(product_name)
                total_subtotal += item["subtotal"]
            
            customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
            if not customer_name:
                customer_name = "Unknown Customer"
            
            transaction_item = TransactionItemModel(
                transaction_id=trans_data["id"],
                transaction_date=trans_data["transaction_date"],
                customer_name=customer_name,
                gender=customer.get("gender"),
                age=customer.get("age"),
                products_name=", ".join(sorted(set(product_names))) if product_names else "No products",
                total_amount=total_subtotal if total_subtotal > 0 else trans_data.get("total_amount", 0)
            )
            
            logger.info(f"Created transaction item: {transaction_item}")
            result.append(transaction_item)
        
        logger.info(f"Returning {len(result)} transaction items")
        return result


    async def get_transactions_data(
        self,
        session: AsyncSession,
        page: int = 1,
        page_size: int = 20
    ) -> PaginatedTransactionItems:
        """Ambil data transaksi pakai ORM SQLAlchemy"""
        
        offset = (page - 1) * page_size

        # Query transaksi + join customer + items + products
        stmt = (
            select(Transaction)
            .options(
                joinedload(Transaction.customer),
                joinedload(Transaction.transaction_items).joinedload(TransactionItem.product)
            )
            .order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
            .offset(offset)
            .limit(page_size)
        )

        result = await session.execute(stmt)
        transactions: list[Transaction] = list(result.scalars().unique().all())
        
        total_items = len(transactions)
        total_pages = math.ceil(total_items / page_size)

        output: list[TransactionItemModel] = []

        for trans in transactions:
            customer = trans.customer
            customer_name = (
                f"{customer.first_name or ''} {customer.last_name or ''}".strip()
                if customer else "Unknown Customer"
            )

            product_names: list[str] = []
            total_subtotal = 0

            for item in trans.transaction_items:
                product_name = item.product.name if item.product else "Unknown"
                product_names.append(product_name)
                total_subtotal += float(item.subtotal or 0)

            output.append(
                TransactionItemModel(
                    transaction_id=str(trans.id),
                    transaction_date=trans.transaction_date,
                    customer_name=customer_name,
                    gender=customer.gender if customer else None,
                    age=customer.age if customer else None,
                    products_name=", ".join(sorted(set(product_names))) if product_names else "No products",
                    total_amount=total_subtotal if total_subtotal > 0 else float(trans.total_amount or 0),
                )
            )
            
        metadata: PaginationMetaData = PaginationMetaData(
            current_page=page,
            page_size=page_size,
            total_pages=total_pages,
            total_items=total_items
        )
        
        response: PaginatedTransactionItems = PaginatedTransactionItems(
            items=output,
            metadata=metadata
        )
        return response


            
    async def get_recent_transactions(self, page: int = 1, page_size: int = DEFAULT_PAGE_SIZE):
        try:
            es_client = await self.get_es_client()
            
            try:
                total_items_response = await es_client.count(index=TRANSACTIONS_INDEX_NAME)
                total_items = total_items_response['count']
            except Exception as e:
                logger.error(f"Error getting transaction count: {e}")
                total_items = 0

            if total_items == 0:
                logger.warning(f"No documents found in index {TRANSACTIONS_INDEX_NAME}")
                return PaginatedTransactionItems(
                    items=[],
                    metadata=PaginationMetaData(
                        current_page=page,
                        page_size=page_size,
                        total_pages=0,
                        total_items=0
                    )
                )

            items: List[TransactionItemModel] = await self.get_transactions_data_with_debug(page=page, page_size=page_size)
            
            total_pages = math.ceil(total_items / page_size)
            current_page = page

            transaction_data: PaginatedTransactionItems = PaginatedTransactionItems(
                items=items,
                metadata=PaginationMetaData(
                    current_page=current_page,
                    page_size=page_size,
                    total_pages=total_pages,
                    total_items=total_items
                )
            )
            return transaction_data
            
        except Exception as e:
            logger.error(f"Error in get_recent_transactions: {e}", exc_info=True)
            return PaginatedTransactionItems(
                items=[],
                metadata=PaginationMetaData(
                    current_page=page,
                    page_size=page_size,
                    total_pages=0,
                    total_items=0
                )
            )
    
    
    def _build_search_query(
        self,
        page: int,
        page_size: int,
        search_query: Optional[str] = None,
        gender_filter: Optional[str] = None,
        min_date: Optional[datetime] = None,
        max_date: Optional[datetime] = None,
    ) -> dict:
        
        must_queries = []
        filter_queries = []
        
        if search_query and search_query.strip():
            must_queries.append({
                "query_string": {
                    "query": search_query,
                    "fields": ["customer_name", "products_name"],
                    "default_operator": "AND"
                }
            })
        
        if gender_filter:
            filter_queries.append({"term": {"gender": gender_filter}})
        
        if min_date or max_date:
            date_range = {}
            if min_date:
                if isinstance(min_date, datetime):
                    date_range["gte"] = min_date.astimezone().replace(tzinfo=None).isoformat()
                else:
                    date_range["gte"] = min_date
            if max_date:
                if isinstance(max_date, datetime):
                    date_range["lte"] = max_date.astimezone().replace(tzinfo=None).isoformat()
                else:
                    date_range["lte"] = max_date
            if date_range:
                filter_queries.append({"range": {"transaction_date": date_range}})
        
        base_query = {"bool": {"must": must_queries or [{"match_all": {}}], "filter": filter_queries}}
        
    
        query_body = {
        "size": 0,  # we only want aggregations
        "query": base_query,
        "aggs": {
            "transactions": {
                "terms": {
                    "field": "id.keyword",
                    "size": page_size,
                    "order": {"latest_transaction_date": "desc"}
                },
                "aggs": {
                    "latest_transaction_date": {"max": {"field": "transaction_date"}},
                    "customer_info": {
                        "top_hits": {
                            "size": 1,
                            "_source": ["customer.first_name", "customer.last_name", "customer.gender", "customer.age"]
                        }
                    },
                    "products_name": {
                        "terms": {"field": "products_name.keyword", "size": 100}
                    },
                    "total_amount": {"sum": {"field": "total_amount"}}
                }
            }
        }
    }
        
        return query_body