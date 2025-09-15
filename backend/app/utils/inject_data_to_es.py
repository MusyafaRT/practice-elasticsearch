import asyncio
import json
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any, List
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import RequestError

# Import your models (assuming they're in a separate file)
from app.db.schemas import Base, User, Customer, ProductCategory, Product, Transaction, TransactionItem

class PostgreSQLToElasticsearchMigrator:
    def __init__(self, 
                 postgres_url: str,
                 elasticsearch_host: str = "localhost:9200"):
        
        # PostgreSQL connection
        self.engine = create_engine(postgres_url)
        self.Session = sessionmaker(bind=self.engine)
        
        # Elasticsearch connection
        self.es = Elasticsearch([elasticsearch_host])
    
    def serialize_value(self, value: Any) -> Any:
        """Convert Python objects to JSON-serializable format"""
        if isinstance(value, uuid.UUID):
            return str(value)
        elif isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, (datetime, date)):
            return value.isoformat()
        elif value is None:
            return None
        return value
    
    def model_to_dict(self, instance) -> Dict[str, Any]:
        """Convert SQLAlchemy model instance to dictionary"""
        result = {}
        for column in instance.__table__.columns:
            value = getattr(instance, column.name)
            result[column.name] = self.serialize_value(value)
        return result
    
    def create_index_mappings(self):
        """Create Elasticsearch index mappings for each table"""
        
        # Users index mapping
        users_mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "first_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "last_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "email": {"type": "keyword"},
                    "oauth_provider": {"type": "keyword"},
                    "oauth_id": {"type": "keyword"},
                    "profile_picture": {"type": "keyword", "index": False},
                    "is_oauth_user": {"type": "boolean"},
                    "is_active": {"type": "boolean"},
                    "last_login": {"type": "date"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
                }
            }
        }
        
        # Customers index mapping
        customers_mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "customer_code": {"type": "keyword"},
                    "first_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "last_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "email": {"type": "keyword"},
                    "phone": {"type": "keyword"},
                    "gender": {"type": "keyword"},
                    "age": {"type": "integer"},
                    "date_of_birth": {"type": "date"},
                    "address": {"type": "text"},
                    "is_active": {"type": "boolean"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
                }
            }
        }
        
        # Product Categories index mapping
        categories_mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "description": {"type": "text"},
                    "is_active": {"type": "boolean"},
                    "created_at": {"type": "date"}
                }
            }
        }
        
        # Products index mapping
        products_mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "description": {"type": "text"},
                    "sku": {"type": "keyword"},
                    "category_id": {"type": "keyword"},
                    "price_per_unit": {"type": "double"},
                    "cost_per_unit": {"type": "double"},
                    "stock_quantity": {"type": "integer"},
                    "min_stock_level": {"type": "integer"},
                    "is_active": {"type": "boolean"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
                }
            }
        }
        
        # Transactions index mapping
        transactions_mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "transaction_number": {"type": "keyword"},
                    "transaction_date": {"type": "date"},
                    "customer_id": {"type": "keyword"},
                    "subtotal": {"type": "double"},
                    "tax_amount": {"type": "double"},
                    "discount_amount": {"type": "double"},
                    "total_amount": {"type": "double"},
                    "created_at": {"type": "date"}
                }
            }
        }
        
        # Transaction Items index mapping
        transaction_items_mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "transaction_id": {"type": "keyword"},
                    "product_id": {"type": "keyword"},
                    "quantity": {"type": "integer"},
                    "price_per_unit": {"type": "double"},
                    "discount_per_unit": {"type": "double"},
                    "subtotal": {"type": "double"},
                    "created_at": {"type": "date"}
                }
            }
        }
        
        return {
            "users": users_mapping,
            "customers": customers_mapping,
            "product_categories": categories_mapping,
            "products": products_mapping,
            "transactions": transactions_mapping,
            "transaction_items": transaction_items_mapping
        }
    
    def create_indices(self):
        """Create Elasticsearch indices with mappings"""
        mappings = self.create_index_mappings()
        
        for index_name, mapping in mappings.items():
            try:
                if self.es.indices.exists(index=index_name):
                    print(f"Index '{index_name}' already exists. Deleting...")
                    self.es.indices.delete(index=index_name)
                
                self.es.indices.create(index=index_name, body=mapping)
                print(f"Created index: {index_name}")
            except RequestError as e:
                print(f"Error creating index {index_name}: {e}")
    
    def bulk_index_data(self, index_name: str, data: List[Dict[str, Any]], batch_size: int = 1000):
        """Bulk index data to Elasticsearch"""
        def generate_docs():
            for doc in data:
                yield {
                    "_index": index_name,
                    "_source": doc
                }
        
        try:
            success, failed = helpers.bulk(
                self.es,
                generate_docs(),
                chunk_size=batch_size,
                request_timeout=60
            )
            print(f"Successfully indexed {success} documents to {index_name}")
            if isinstance(failed, list) and failed:
                print(f"Failed to index {len(failed)} documents to {index_name}")
        except Exception as e:
            print(f"Error during bulk indexing to {index_name}: {e}")
    
    def migrate_table(self, model_class, index_name: str, batch_size: int = 1000):
        """Migrate a single table to Elasticsearch"""
        session = self.Session()
        try:
            print(f"Starting migration for {model_class.__name__}...")
            
            # Get total count for progress tracking
            total_count = session.query(model_class).count()
            print(f"Total records to migrate: {total_count}")
            
            # Process in batches
            offset = 0
            while offset < total_count:
                batch = session.query(model_class).offset(offset).limit(batch_size).all()
                if not batch:
                    break
                
                # Convert to dictionaries
                docs = [self.model_to_dict(instance) for instance in batch]
                
                # Bulk index
                self.bulk_index_data(index_name, docs)
                
                offset += len(batch)
                print(f"Migrated {min(offset, total_count)}/{total_count} records from {model_class.__name__}")
            
            print(f"Completed migration for {model_class.__name__}")
            
        except Exception as e:
            print(f"Error migrating {model_class.__name__}: {e}")
        finally:
            session.close()
    
    def migrate_all(self, batch_size: int = 1000):
        """Migrate all tables to Elasticsearch"""
        print("Starting full migration from PostgreSQL to Elasticsearch...")
        
        # Create indices
        self.create_indices()
        
        # Define migration order (important for referential integrity in search)
        migrations = [
            (User, "users"),
            (ProductCategory, "product_categories"),
            (Customer, "customers"),
            (Product, "products"),
            (Transaction, "transactions"),
            (TransactionItem, "transaction_items")
        ]
        
        # Migrate each table
        for model_class, index_name in migrations:
            self.migrate_table(model_class, index_name, batch_size)
        
        print("Migration completed!")
    
    def create_enriched_indices(self):
        """Create enriched documents with joined data for better search experience"""
        print("Creating enriched indices...")
        
        session = self.Session()
        try:
            # Enriched products with category information
            products_with_category = session.query(Product, ProductCategory).join(ProductCategory).all()
            enriched_products = []
            
            for product, category in products_with_category:
                product_dict = self.model_to_dict(product)
                product_dict['category_name'] = category.name
                product_dict['category_description'] = category.description
                enriched_products.append(product_dict)
            
            # Create enriched products index
            enriched_products_mapping = {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                        "description": {"type": "text"},
                        "sku": {"type": "keyword"},
                        "category_id": {"type": "keyword"},
                        "category_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                        "category_description": {"type": "text"},
                        "price_per_unit": {"type": "double"},
                        "cost_per_unit": {"type": "double"},
                        "stock_quantity": {"type": "integer"},
                        "min_stock_level": {"type": "integer"},
                        "is_active": {"type": "boolean"},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"}
                    }
                }
            }
            
            if self.es.indices.exists(index="products_enriched"):
                self.es.indices.delete(index="products_enriched")
            
            self.es.indices.create(index="products_enriched", body=enriched_products_mapping)
            self.bulk_index_data("products_enriched", enriched_products)
            
            # Enriched transactions with customer and item details
            transactions_with_details = session.query(Transaction).join(Customer).all()
            enriched_transactions = []
            
            for transaction in transactions_with_details:
                trans_dict = self.model_to_dict(transaction)
                trans_dict['customer_name'] = f"{transaction.customer.first_name} {transaction.customer.last_name}".strip()
                trans_dict['customer_email'] = transaction.customer.email
                trans_dict['customer_code'] = transaction.customer.customer_code
                
                # Add transaction items
                items = []
                for item in transaction.transaction_items:
                    item_dict = self.model_to_dict(item)
                    item_dict['product_name'] = item.product.name
                    item_dict['product_sku'] = item.product.sku
                    items.append(item_dict)
                
                trans_dict['items'] = items
                trans_dict['items_count'] = len(items)
                enriched_transactions.append(trans_dict)
            
            # Create enriched transactions index
            enriched_transactions_mapping = {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "transaction_number": {"type": "keyword"},
                        "transaction_date": {"type": "date"},
                        "customer_id": {"type": "keyword"},
                        "customer_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                        "customer_email": {"type": "keyword"},
                        "customer_code": {"type": "keyword"},
                        "subtotal": {"type": "double"},
                        "tax_amount": {"type": "double"},
                        "discount_amount": {"type": "double"},
                        "total_amount": {"type": "double"},
                        "items_count": {"type": "integer"},
                        "created_at": {"type": "date"},
                        "items": {
                            "type": "nested",
                            "properties": {
                                "id": {"type": "keyword"},
                                "product_id": {"type": "keyword"},
                                "product_name": {"type": "text"},
                                "product_sku": {"type": "keyword"},
                                "quantity": {"type": "integer"},
                                "price_per_unit": {"type": "double"},
                                "discount_per_unit": {"type": "double"},
                                "subtotal": {"type": "double"}
                            }
                        }
                    }
                }
            }
            
            if self.es.indices.exists(index="transactions_enriched"):
                self.es.indices.delete(index="transactions_enriched")
            
            self.es.indices.create(index="transactions_enriched", body=enriched_transactions_mapping)
            self.bulk_index_data("transactions_enriched", enriched_transactions)
            
            print("Enriched indices created successfully!")
            
        except Exception as e:
            print(f"Error creating enriched indices: {e}")
        finally:
            session.close()

# Usage example
def main():
    # Configuration
    POSTGRES_URL = "postgresql://ecommerce:Niffier2025@localhost:5433/ecommerce"
    ELASTICSEARCH_HOST = "http://localhost:9200"
    
    # Create migrator instance
    migrator = PostgreSQLToElasticsearchMigrator(
        postgres_url=POSTGRES_URL,
        elasticsearch_host=ELASTICSEARCH_HOST,
    )
    
    # Run migration
    try:
        # Basic migration - mirror PostgreSQL structure
        migrator.migrate_all(batch_size=1000)
        
        # Optional: Create enriched indices for better search experience
        migrator.create_enriched_indices()
        
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    main()