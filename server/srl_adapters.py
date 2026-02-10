"""
SRL Adapters - Protocol-specific adapters for fetching data from external resources

PHILOSOPHY:
Each adapter knows how to connect to a specific type of resource and fetch data.
Adapters are PASSIVE - they only fetch when invoked, never cache unless requested.

SECURITY:
- Credentials decrypted only in memory during fetch
- Never logged or exposed
- Connection pooling for efficiency
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import json
import time
from datetime import datetime


class SRLAdapter(ABC):
    """Base class for all SRL adapters."""
    
    def __init__(self, connection_string: str, credentials: Dict[str, Any], config: Dict[str, Any]):
        """
        Initialize adapter.
        
        Args:
            connection_string: Resource connection string
            credentials: Decrypted credentials
            config: Adapter configuration
        """
        self.connection_string = connection_string
        self.credentials = credentials
        self.config = config or {}
        self.timeout = self.config.get("timeout", 30)
        self.max_retries = self.config.get("max_retries", 3)
    
    @abstractmethod
    def fetch(self, query: Optional[str] = None, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Fetch data from resource.
        
        Args:
            query: Query string (SQL, API endpoint, file path, etc.)
            parameters: Additional parameters
        
        Returns:
            {
                "data": <fetched data>,
                "metadata": {
                    "size_bytes": <size>,
                    "rows": <row count>,
                    "duration_ms": <duration>
                }
            }
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if connection is valid."""
        pass
    
    def close(self):
        """Close connection (if applicable)."""
        pass


# ============================================================================
# DATABASE ADAPTERS
# ============================================================================

class PostgreSQLAdapter(SRLAdapter):
    """Adapter for PostgreSQL databases."""
    
    def __init__(self, connection_string: str, credentials: Dict[str, Any], config: Dict[str, Any]):
        super().__init__(connection_string, credentials, config)
        self.pool = None
    
    def fetch(self, query: Optional[str] = None, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute SQL query and return results."""
        try:
            import psycopg2
            from psycopg2 import pool
            
            start_time = time.time()
            
            # Create connection pool if not exists
            if not self.pool:
                self.pool = pool.SimpleConnectionPool(
                    1, 10,
                    self.connection_string,
                    user=self.credentials.get("username"),
                    password=self.credentials.get("password")
                )
            
            # Get connection from pool
            conn = self.pool.getconn()
            cursor = conn.cursor()
            
            # Execute query
            cursor.execute(query, parameters or {})
            
            # Fetch results
            if cursor.description:  # SELECT query
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                data = [dict(zip(columns, row)) for row in rows]
                row_count = len(rows)
            else:  # INSERT/UPDATE/DELETE
                conn.commit()
                data = {"affected_rows": cursor.rowcount}
                row_count = cursor.rowcount
            
            cursor.close()
            self.pool.putconn(conn)
            
            duration_ms = (time.time() - start_time) * 1000
            
            return {
                "data": data,
                "metadata": {
                    "size_bytes": len(json.dumps(data)),
                    "rows": row_count,
                    "duration_ms": duration_ms
                }
            }
        
        except Exception as e:
            raise Exception(f"PostgreSQL fetch failed: {str(e)}")
    
    def test_connection(self) -> bool:
        """Test PostgreSQL connection."""
        try:
            result = self.fetch("SELECT 1")
            return result["data"][0]["?column?"] == 1
        except:
            return False
    
    def close(self):
        """Close connection pool."""
        if self.pool:
            self.pool.closeall()


class MongoDBAdapter(SRLAdapter):
    """Adapter for MongoDB databases."""
    
    def __init__(self, connection_string: str, credentials: Dict[str, Any], config: Dict[str, Any]):
        super().__init__(connection_string, credentials, config)
        self.client = None
    
    def fetch(self, query: Optional[str] = None, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute MongoDB query and return results."""
        try:
            from pymongo import MongoClient
            
            start_time = time.time()
            
            # Create client if not exists
            if not self.client:
                self.client = MongoClient(
                    self.connection_string,
                    username=self.credentials.get("username"),
                    password=self.credentials.get("password"),
                    serverSelectionTimeoutMS=self.timeout * 1000
                )
            
            # Parse query (JSON format)
            query_obj = json.loads(query) if isinstance(query, str) else query
            
            db_name = query_obj.get("database")
            collection_name = query_obj.get("collection")
            operation = query_obj.get("operation", "find")
            filter_obj = query_obj.get("filter", {})
            
            # Get collection
            db = self.client[db_name]
            collection = db[collection_name]
            
            # Execute operation
            if operation == "find":
                cursor = collection.find(filter_obj)
                data = list(cursor)
                row_count = len(data)
            elif operation == "find_one":
                data = collection.find_one(filter_obj)
                row_count = 1 if data else 0
            else:
                raise ValueError(f"Unsupported operation: {operation}")
            
            duration_ms = (time.time() - start_time) * 1000
            
            return {
                "data": data,
                "metadata": {
                    "size_bytes": len(json.dumps(data, default=str)),
                    "rows": row_count,
                    "duration_ms": duration_ms
                }
            }
        
        except Exception as e:
            raise Exception(f"MongoDB fetch failed: {str(e)}")
    
    def test_connection(self) -> bool:
        """Test MongoDB connection."""
        try:
            from pymongo import MongoClient
            if not self.client:
                self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            self.client.server_info()
            return True
        except:
            return False
    
    def close(self):
        """Close MongoDB client."""
        if self.client:
            self.client.close()


# ============================================================================
# API ADAPTERS
# ============================================================================

class RESTAPIAdapter(SRLAdapter):
    """Adapter for REST APIs."""

    def fetch(self, query: Optional[str] = None, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make HTTP request to REST API."""
        try:
            import requests

            start_time = time.time()

            # Parse parameters
            params = parameters or {}
            method = params.get("method", "GET").upper()
            endpoint = query or params.get("endpoint", "")
            headers = params.get("headers", {})
            body = params.get("body")

            # Add authentication
            auth_method = self.credentials.get("auth_method", "none")
            if auth_method == "bearer":
                headers["Authorization"] = f"Bearer {self.credentials.get('token')}"
            elif auth_method == "api_key":
                key_name = self.credentials.get("key_name", "X-API-Key")
                headers[key_name] = self.credentials.get("api_key")
            elif auth_method == "basic":
                auth = (self.credentials.get("username"), self.credentials.get("password"))
            else:
                auth = None

            # Build URL
            url = f"{self.connection_string.rstrip('/')}/{endpoint.lstrip('/')}"

            # Make request
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=body if method in ["POST", "PUT", "PATCH"] else None,
                params=params.get("query_params"),
                auth=auth if auth_method == "basic" else None,
                timeout=self.timeout
            )

            response.raise_for_status()

            # Parse response
            try:
                data = response.json()
            except:
                data = response.text

            duration_ms = (time.time() - start_time) * 1000

            return {
                "data": data,
                "metadata": {
                    "size_bytes": len(response.content),
                    "status_code": response.status_code,
                    "duration_ms": duration_ms
                }
            }

        except Exception as e:
            raise Exception(f"REST API fetch failed: {str(e)}")

    def test_connection(self) -> bool:
        """Test API connection."""
        try:
            result = self.fetch(query="", parameters={"method": "GET"})
            return result["metadata"]["status_code"] < 400
        except:
            return False


# ============================================================================
# FILE ADAPTERS
# ============================================================================

class FileAdapter(SRLAdapter):
    """Adapter for local files."""

    def fetch(self, query: Optional[str] = None, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Read file content."""
        try:
            start_time = time.time()

            # Get file path
            file_path = query or parameters.get("path")
            mode = parameters.get("mode", "r") if parameters else "r"
            encoding = parameters.get("encoding", "utf-8") if parameters else "utf-8"

            # Read file
            if "b" in mode:
                with open(file_path, mode) as f:
                    data = f.read()
                size_bytes = len(data)
            else:
                with open(file_path, mode, encoding=encoding) as f:
                    data = f.read()
                size_bytes = len(data.encode(encoding))

            duration_ms = (time.time() - start_time) * 1000

            return {
                "data": data,
                "metadata": {
                    "size_bytes": size_bytes,
                    "duration_ms": duration_ms
                }
            }

        except Exception as e:
            raise Exception(f"File fetch failed: {str(e)}")

    def test_connection(self) -> bool:
        """Test file access."""
        try:
            import os
            return os.path.exists(self.connection_string)
        except:
            return False


# ============================================================================
# ADAPTER FACTORY
# ============================================================================

ADAPTER_REGISTRY = {
    "postgresql": PostgreSQLAdapter,
    "postgres": PostgreSQLAdapter,
    "mongodb": MongoDBAdapter,
    "mongo": MongoDBAdapter,
    "http": RESTAPIAdapter,
    "https": RESTAPIAdapter,
    "rest": RESTAPIAdapter,
    "file": FileAdapter,
    "local": FileAdapter,
}


def get_adapter(protocol: str, connection_string: str, credentials: Dict[str, Any], config: Dict[str, Any]) -> SRLAdapter:
    """
    Get appropriate adapter for protocol.

    Args:
        protocol: Protocol name (postgresql, mongodb, http, etc.)
        connection_string: Connection string
        credentials: Decrypted credentials
        config: Adapter configuration

    Returns:
        Adapter instance

    Raises:
        ValueError: If protocol not supported
    """
    adapter_class = ADAPTER_REGISTRY.get(protocol.lower())
    if not adapter_class:
        raise ValueError(f"Unsupported protocol: {protocol}. Supported: {list(ADAPTER_REGISTRY.keys())}")

    return adapter_class(connection_string, credentials, config)


def get_supported_protocols() -> List[str]:
    """Get list of supported protocols."""
    return list(ADAPTER_REGISTRY.keys())
