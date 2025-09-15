import asyncio
import logging
from elasticsearch.helpers import async_streaming_bulk
from app.db.elastic import get_async_es_client

# Configuration
ENRICHED_INDEX_NAME = "enriched_transactions"
TRANSACTIONS_INDEX = "transactions"
CUSTOMERS_INDEX = "customers"
TRANSACTION_ITEMS_INDEX = "transaction_items"
PRODUCTS_INDEX = "products"

BATCH_SIZE = 1000

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_enriched_index():
    """Creates the enriched_transactions index with a specific mapping."""
    es_client = await get_async_es_client()
    if not await es_client.indices.exists(index=ENRICHED_INDEX_NAME):
        logger.info(f"Creating index '{ENRICHED_INDEX_NAME}'...")
        mapping = {
            "properties": {
                "transaction_id": {"type": "keyword"},
                "transaction_date": {"type": "date"},
                "customer_id": {"type": "keyword"},
                "customer_name": {"type": "text"},
                "gender": {"type": "keyword"},
                "age": {"type": "integer"},
                "total_amount": {"type": "float"},
                "products": {
                    "type": "nested",
                    "properties": {
                        "product_id": {"type": "keyword"},
                        "product_name": {"type": "text"},
                        "quantity": {"type": "integer"},
                        "subtotal": {"type": "float"}
                    }
                },
                "products_name": {"type": "text"}
            }
        }
        await es_client.indices.create(index=ENRICHED_INDEX_NAME, mappings=mapping)
        logger.info("Index created successfully.")
    else:
        logger.info(f"Index '{ENRICHED_INDEX_NAME}' already exists.")

async def enrich_data():
    """Fetches, enriches, and indexes transaction data."""
    es_client = await get_async_es_client()
    logger.info("Starting data enrichment process...")

    # 1. Fetch all necessary data
    logger.info("Fetching data from source indices...")
    customers = {c['_id']: c['_source'] async for c in es_scan(es_client, CUSTOMERS_INDEX)}
    products = {p['_id']: p['_source'] async for p in es_scan(es_client, PRODUCTS_INDEX)}
    
    logger.info(f"Found {len(customers)} customers and {len(products)} products.")

    # 2. Process transactions in batches
    async for doc in async_streaming_bulk(es_client, enriched_transaction_generator(customers, products)):
        pass

    logger.info("Data enrichment process completed.")

async def es_scan(client, index):
    """Helper to scroll through all documents in an index."""
    scroll = "2m"
    response = await client.search(index=index, scroll=scroll, size=1000, body={"query": {"match_all": {}}})
    
    old_scroll_id = response["_scroll_id"]
    
    while len(response["hits"]["hits"]):
        for hit in response["hits"]["hits"]:
            yield hit
            
        response = await client.scroll(scroll_id=old_scroll_id, scroll=scroll)
        old_scroll_id = response["_scroll_id"]

async def enriched_transaction_generator(customers, products):
    """Generator function to yield enriched transaction documents for bulk indexing."""
    es_client = await get_async_es_client()
    
    async for trans in es_scan(es_client, TRANSACTIONS_INDEX):
        trans_id = trans['_source']['id']
        trans_data = trans['_source']
        
        # Get customer info
        customer = customers.get(str(trans_data.get("customer_id", "")))
        
        # Get transaction items
        items_query = {"query": {"term": {"transaction_id": trans_id}}, "size": 1000}
        items_result = await es_client.search(index=TRANSACTION_ITEMS_INDEX, body=items_query)
        
        product_list = []
        product_names = []
        total_subtotal = 0

        for item in items_result["hits"]["hits"]:
            item_source = item['_source']
            product = products.get(str(item_source.get("product_id")))
            if product:
                product_list.append({
                    "product_id": item_source.get("product_id"),
                    "product_name": product.get("name"),
                    "quantity": item_source.get("quantity", 1),
                    "subtotal": item_source.get("subtotal")
                })
                product_names.append(product.get("name"))
                total_subtotal += item_source.get("subtotal", 0)

        customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip() if customer else "Unknown"

        doc = {
            "_index": ENRICHED_INDEX_NAME,
            "_id": trans_id,
            "_source": {
                "transaction_id": trans_id,
                "transaction_date": trans_data.get("transaction_date"),
                "customer_id": trans_data.get("customer_id"),
                "customer_name": customer_name,
                "gender": customer.get("gender") if customer else None,
                "age": customer.get("age") if customer else None,
                "products": product_list,
                "products_name": ", ".join(sorted(set(product_names))),
                "total_amount": total_subtotal or trans_data.get("total_amount", 0)
            }
        }
        yield doc

async def main():
    await create_enriched_index()
    await enrich_data()

if __name__ == "__main__":
    asyncio.run(main())
