from elasticsearch import Elasticsearch, helpers
import csv
from datetime import datetime
import ast

# ======================
# 1. Normalize date dengan aman
# ======================
from datetime import datetime
from dateutil import parser

def normalize_date(value):
    if not value or value.strip() == "":
        return None
    try:
        # Gunakan parser otomatis, termasuk timezone
        dt = parser.parse(value)
        return dt.isoformat()  # Menghasilkan ISO 8601 dengan offset
    except Exception:
        return None


# ======================
# 2. Connect ke Elasticsearch
# ======================
es = Elasticsearch("http://localhost:9200")
INDEX_NAME = "news"
CSV_FILE = "../news_data.csv"  # Adjust sesuai path CSV

# ======================
# 3. Mapping untuk index
# ======================
mapping = {
    "settings": {
        "analysis": {
        "analyzer": {
            "indonesian_custom": {
            "tokenizer": "standard",
            "filter": ["lowercase", "indonesian_stop"]
            }
        },
        "filter": {
            "indonesian_stop": {
            "type": "stop",
            "stopwords": "_indonesian_"
            }
        }
        }
    },
    "mappings": {
        "properties": {
            "title": {
                "type": "text", 
                "fielddata": True, 
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }, 
                    "indonesian_words": {
                        "type": "text",
                        "analyzer": "indonesian_custom",
                        "fielddata": True
                    }
                }
            },
            "author": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "publish_date": {"type": "date", "format": "strict_date_optional_time||yyyy-MM-dd||yyyy-MM-dd HH:mm:ss||epoch_millis"},
            "article_text": {
                "type": "text",
                "fielddata": True,
                "fields": {
                    "indonesian_words": {
                    "type": "text",
                    "analyzer": "indonesian_custom",
                    "fielddata": True
                    }
                }
            },
            "url": {"type": "keyword"},
            "main_image": {"type": "keyword"},
            "tag": {"type": "keyword"}
        }
    }
}

# ======================
# 4. Recreate index
# ======================
if es.indices.exists(index=INDEX_NAME):
    print(f"Deleting old index: {INDEX_NAME}")
    es.indices.delete(index=INDEX_NAME)

print(f"Creating index: {INDEX_NAME}")
es.indices.create(index=INDEX_NAME, body=mapping)

# ======================
# 5. Convert CSV → Actions untuk bulk
# ======================
def csv_to_actions(file_path, index_name):
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            clean_row = {}

            # Map CSV columns → Elasticsearch fields
            clean_row["title"] = row.get("title", "").strip() or None
            clean_row["author"] = row.get("author", "").strip() or None
            clean_row["article_text"] = row.get("article_text", "").strip() or None
            clean_row["url"] = row.get("url", "").strip() or None
            clean_row["main_image"] = row.get("main_image", "").strip() or None
            raw_tag = row.get("tag", "").strip()
            if raw_tag:
                try:
                    # Convert stringified array into real Python list
                    clean_row["tag"] = [t.strip() for t in ast.literal_eval(raw_tag)]
                except Exception:
                    # fallback: if parsing fails, put it as single-element list
                    clean_row["tag"] = [raw_tag]


            # Normalize publish_date
            publish_date = row.get("publish_date", "").strip()
            clean_row["publish_date"] = normalize_date(publish_date)

            # Hapus field None agar Elasticsearch tidak error
            clean_row = {k: v for k, v in clean_row.items() if v is not None}

            # Gunakan ID unik dari nomor baris
            doc_id = f"doc_{i+1}"

            yield {
                "_index": index_name,
                "_id": doc_id,
                "_source": clean_row
            }

# ======================
# 6. Bulk import ke Elasticsearch
# ======================
try:
    print("Starting bulk import...")
    success_count, failed_items = helpers.bulk(
        es,
        csv_to_actions(CSV_FILE, INDEX_NAME),
        chunk_size=500,
        request_timeout=120
    )
    print(f"✅ Import completed successfully! Documents indexed: {success_count}")

    # Refresh index supaya bisa langsung dicari
    es.indices.refresh(index=INDEX_NAME)

    # Count total documents
    count = es.count(index=INDEX_NAME)
    print(f"📈 Total documents in index: {count['count']}")

except helpers.BulkIndexError as e:
    print(f"❌ {len(e.errors)} documents failed to import")
    print("First 5 errors:")
    for error in e.errors[:5]:
        print(error)

except Exception as e:
    print(f"❌ Unexpected error: {e}")

# ======================
# 7. Optional: Test query
# ======================
try:
    test_query = {"query": {"match_all": {}}, "size": 1}
    result = es.search(index=INDEX_NAME, body=test_query)
    if result['hits']['total']['value'] > 0:
        print("\n🔍 Sample document:")
        sample_doc = result['hits']['hits'][0]['_source']
        for k, v in sample_doc.items():
            print(f"  {k}: {str(v)[:100]}{'...' if len(str(v)) > 100 else ''}")

except Exception as e:
    print(f"⚠️ Could not retrieve sample document: {e}")
