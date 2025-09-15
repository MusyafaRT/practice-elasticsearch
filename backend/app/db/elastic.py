from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

def get_es_client():
    return es
