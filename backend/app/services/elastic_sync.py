from typing import Any, Dict, Callable, Tuple, List
from sqlalchemy import text
from elasticsearch import helpers
import asyncio
import logging

logger = logging.getLogger(__name__)


class ElasticSyncService:
    def __init__(self, es_client, db_session_factory):
        self.es = es_client
        self.db_session_factory = db_session_factory

    async def ensure_index(self, index_name: str, mapping: Dict[str, Any]) -> None:
        try:
            if not self.es.indices.exists(index=index_name):
                self.es.indices.create(index=index_name, body=mapping)
                logger.info(f"✅ Created index: {index_name}")
        except Exception as e:
            logger.error(f"❌ Error creating index {index_name}: {str(e)}")
            raise

    async def sync_to_es(
        self,
        index_name: str,
        query: Any,
        transform_func: Callable[[Any], Tuple[Dict[str, Any], str]],
        mapping: Dict[str, Any] | None = None,
    ) -> int:
        async with self.db_session_factory() as session:
            try:
                if isinstance(query, str):
                    result = await session.execute(text(query))
                    rows = result.fetchall()
                else:
                    result = await session.execute(query)
                    try:
                        rows = result.scalars().all()
                    except Exception:
                        rows = result.mappings().all()

                if not rows:
                    logger.info(f"No data found for {index_name}")
                    return 0

                if not self.es.ping():
                    raise ConnectionError("Cannot connect to Elasticsearch")

                # Ensure index if mapping provided
                if mapping:
                    await self.ensure_index(index_name, mapping)

                actions = [
                    {
                        "_index": index_name,
                        "_id": doc_id,
                        "_source": source,
                    }
                    for row in rows
                    for source, doc_id in [transform_func(row)]
                ]

                success_count, failed_actions = await asyncio.to_thread(
                    helpers.bulk,
                    self.es,
                    actions,
                    index=index_name,
                    raise_on_error=False,
                    raise_on_exception=False,
                )

                if failed_actions:
                    logger.warning(f"⚠️ Failed to index docs in {index_name}: {failed_actions}")

                logger.info(f"✅ Synced {success_count} records → {index_name}")
                return success_count

            except Exception as e:
                logger.error(f"❌ Sync error for {index_name}: {str(e)}")
                await session.rollback()
                raise
            finally:
                await session.close()
