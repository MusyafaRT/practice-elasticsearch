from app.db.elastic import get_es_client
from app.db.postgresql import AsyncSessionLocal
from app.services.elastic_sync import ElasticSyncService
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dateutil.relativedelta import relativedelta
from fastapi import HTTPException, status

ES_INDEX = "news"

class NewsAnalyticsService:
    def __init__(self):
        self.es = get_es_client()
        self.elastic_sync = ElasticSyncService(self.es, AsyncSessionLocal)
        
    def _build_base_query(self, search_query: Optional[str] = None, 
                         start_date: Optional[datetime] = None, 
                         end_date: Optional[datetime] = None) -> Dict[str, Any]:
        must_clauses = []
        
        if search_query:
            must_clauses.append({
                "query_string": {
                    "query": search_query,
                    "fields": ["title^2", "article_text", "tag"],
                    "default_operator": "AND"  
                }
            })

        
        if start_date or end_date:
            date_range = {}
            if start_date:
                date_range["gte"] = start_date
            if end_date:
                date_range["lte"] = end_date
            must_clauses.append({"range": {"publish_date": date_range}})
        
        if must_clauses:
            return {"bool": {"must": must_clauses}}
        else:
            return {"match_all": {}}

    def get_top_title_keywords(self, size: int = 10, search_query: Optional[str] = None,
                              start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        query = self._build_base_query(search_query, start_date, end_date)
        
        resp = self.es.search(
            index=ES_INDEX,
            body={
                "size": 0,
                "query": query,
                "aggs": {
                    "title_keywords": {
                        "terms": {
                            "field": "title.indonesian_words",
                            "size": size
                        }
                    }
                }
            }
        )
        return [{"keyword": b["key"], "count": b["doc_count"]} 
                for b in resp["aggregations"]["title_keywords"]["buckets"]]

    def get_tag_distribution(self, size: int = 20, search_query: Optional[str] = None,
                           start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        query = self._build_base_query(search_query, start_date, end_date)
        
        resp = self.es.search(
            index=ES_INDEX,
            body={
                "size": 0,
                "query": query,
                "aggs": {
                    "tags": {
                        "terms": {
                            "field": "tag",
                            "size": size
                        }
                    }
                }
            }
        )
        return [{"tag": b["key"], "count": b["doc_count"]} 
                for b in resp["aggregations"]["tags"]["buckets"]]

    def get_timeline(self, interval: str = "week", search_query: Optional[str] = None,
                    start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        query = self._build_base_query(search_query, start_date, end_date)
        
        if not start_date and not end_date:
            if query.get("match_all"):
                query = {
                    "range": {
                        "publish_date": {
                            "gte": "2020-01-01T00:00:00Z",
                            "lte": "2024-12-12T00:00:00Z"
                        }
                    }
                }
        if start_date and end_date:
            diff = relativedelta(end_date, start_date)
            total_months = diff.years * 12 + diff.months
            if total_months < 2:
                interval = "day"
        
        resp = self.es.search(
            index=ES_INDEX,
            body={
                "size": 0,
                "query": query,
                "aggs": {
                    "timeline": {
                        "date_histogram": {
                            "field": "publish_date",
                            "calendar_interval": interval,
                            "min_doc_count": 0,
                        }
                    }
                }
            }
        )
        return [{"date": b["key_as_string"], "count": b["doc_count"]} 
                for b in resp["aggregations"]["timeline"]["buckets"]]

    def get_top_keywords(self, field: str = "article_text.indonesian_words", size: int = 10,
                        search_query: Optional[str] = None, start_date: Optional[datetime] = None, 
                        end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'shall', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me',
            'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our',
            'their', 'yang', 'dari', 'dan', 'di', 'ke', 'untuk', 'pada', 'dengan',
            'adalah', 'akan', 'telah', 'sudah', 'juga', 'tidak', 'ini', 'itu',
            'atau', 'saja', 'bisa', 'dapat', 'harus', 'masih', 'lebih', 'karena'
        }

        html_noise = {
            'img', 'src', 'href', 'alt', 'class', 'id', 'div', 'span', 'width', 
            'height', 'style', 'px', 'rgb', 'rgba', 'https', 'http', 'www',
            'jpg', 'jpeg', 'png', 'gif', 'css', 'js', 'html', 'htm'
        }

        excluded_words = {w.lower() for w in stop_words | html_noise}
        query = self._build_base_query(search_query, start_date, end_date)

        resp = self.es.search(
            index=ES_INDEX,
            body={
                "size": 0,
                "query": query,
                "aggs": {
                    "keywords": {
                        "terms": {
                            "field": field,
                            "size": size * 5,
                            "min_doc_count": 3,
                            "exclude": list(excluded_words)
                        }
                    }
                }
            }
        )

        buckets = resp["aggregations"]["keywords"]["buckets"][:size]
        total_count = sum(b["doc_count"] for b in buckets) or 1

        return [
            {
                "keyword": b["key"],
                "count": b["doc_count"],
                "percent": round(b["doc_count"] / total_count * 100, 2)
            }
            for b in buckets
        ]

    def get_recent_news(
        self, 
        size: int = 10, 
        search_query: Optional[str] = None,
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None,
        search_after: Optional[List[Any]] = None
    ):
        query = self._build_base_query(search_query, start_date, end_date)
        body={
            "size": size,
            "query": query,
            "sort": [{"publish_date": {"order": "desc"}}],
            "_source": ["title", "author", "publish_date", "url", "main_image", "tag"]
        }
        
        if search_after:
            body["search_after"] = search_after
            
        
        resp = self.es.search(index=ES_INDEX,body=body)
        hits = [hit["_source"] for hit in resp["hits"]["hits"]]

        next_search_after = resp["hits"]["hits"][-1]["sort"] if resp["hits"]["hits"] else None


        return hits, next_search_after



    def get_statistics(self, search_query: Optional[str] = None,
                      start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        query = self._build_base_query(search_query, start_date, end_date)
        
        resp = self.es.search(
            index=ES_INDEX,
            body={
                "size": 0,
                "query": query,
                "aggs": {
                    "total_articles": {"value_count": {"field": "title"}},
                    "unique_authors": {"cardinality": {"field": "author.keyword"}},
                    "unique_tags": {"cardinality": {"field": "tag"}},
                    "date_stats": {"stats": {"field": "publish_date"}}
                }
            }
        )
        
        aggs = resp["aggregations"]
        date_stats = aggs["date_stats"]
        
        return {
            "total_articles": aggs["total_articles"]["value"],
            "unique_authors": aggs["unique_authors"]["value"],
            "unique_tags": aggs["unique_tags"]["value"],
            "date_range": {
                "earliest": date_stats.get("min_as_string"),
                "latest": date_stats.get("max_as_string")
            } if date_stats["count"] > 0 else None
        }

    def get_overview(
        self,
        search_query: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        try:
            data = {
                "statistics": self.get_statistics(search_query, start_date, end_date),
                "top_title_keywords": self.get_top_title_keywords(10, search_query, start_date, end_date),
                "tag_distribution": self.get_tag_distribution(50, search_query, start_date, end_date),
                "timeline": self.get_timeline("week", search_query, start_date, end_date),
                "top_keywords": self.get_top_keywords("article_text.indonesian_words", 15, search_query, start_date, end_date),
            }

            if not data["statistics"]["total_articles"]:
                raise HTTPException(
                    status_code=status.HTTP_204_NO_CONTENT,
                    detail="No content available for the given parameters"
                )

            return data

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )


