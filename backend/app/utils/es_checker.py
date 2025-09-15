import asyncio
from elasticsearch import AsyncElasticsearch

ES_HOST = "http://localhost:9200"
INDEX_NAME = "transactions"

async def fetch_transactions():
    es = AsyncElasticsearch(hosts=[ES_HOST])
    
    # Ping to check connection
    if not await es.ping():
        print("❌ Elasticsearch is not available")
        return

    # Fetch first 5 documents
    resp = await es.search(
        index=INDEX_NAME,
        body={
            "size": 5,
            "_source": ["id", "transaction_date", "customer", "transaction_items", "total_amount"]
        }
    )
    
    hits = resp["hits"]["hits"]
    print(f"Found {len(hits)} documents:")
    for hit in hits:
        print(hit["_source"])

    await es.close()

asyncio.run(fetch_transactions())
