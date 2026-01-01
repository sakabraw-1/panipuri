import os
import duckdb
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
DUCKDB_PATH = os.getenv("DUCKDB_PATH", "../data/panipuri.duckdb")

class KnowledgeGraphIngestor:
    def __init__(self, uri, user, password, duckdb_path):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.duckdb_conn = duckdb.connect(duckdb_path, read_only=True)

    def close(self):
        self.driver.close()
        self.duckdb_conn.close()

    def apply_schema(self, schema_file="kg/schema.cypher"):
        """Applies constraints and indexes from the schema file."""
        print(f"Applying schema from {schema_file}...")
        with open(schema_file, "r") as f:
            queries = f.read().split(";")
        
        with self.driver.session() as session:
            for query in queries:
                if query.strip():
                    session.run(query)
        print("Schema applied.")

    def ingest_countries(self):
        """Ingests unique countries from the trade data."""
        print("Ingesting Countries...")
        query = """
        SELECT DISTINCT reporter_iso as iso_code FROM harmonized_trade_flows
        UNION
        SELECT DISTINCT partner_iso as iso_code FROM harmonized_trade_flows
        """
        countries = self.duckdb_conn.execute(query).fetchall()

        cypher = """
        MERGE (c:Country {iso3_code: $iso_code})
        ON CREATE SET c.name = $iso_code  -- Placeholder, enrich later
        """
        
        with self.driver.session() as session:
            for row in countries:
                session.run(cypher, iso_code=row[0])
        print(f"Ingested {len(countries)} countries.")

    def ingest_sectors(self):
        """Ingests unique sectors from the harmonized data."""
        print("Ingesting Sectors...")
        query = "SELECT DISTINCT sector_id FROM harmonized_trade_flows"
        sectors = self.duckdb_conn.execute(query).fetchall()

        cypher = """
        MERGE (s:Sector {id: $sector_id})
        ON CREATE SET s.name = $sector_id -- Placeholder
        """

        with self.driver.session() as session:
            for row in sectors:
                session.run(cypher, sector_id=row[0])
        print(f"Ingested {len(sectors)} sectors.")

    def ingest_trade_flows(self):
        """Ingests harmonized trade flows as edges."""
        print("Ingesting Trade Flows...")
        # Aggregate flows by year, reporter, partner, sector
        query = """
        SELECT 
            year, 
            reporter_iso, 
            partner_iso, 
            sector_id, 
            SUM(harmonized_value) as total_value 
        FROM harmonized_trade_flows
        GROUP BY year, reporter_iso, partner_iso, sector_id
        """
        flows = self.duckdb_conn.execute(query).fetchall()

        cypher = """
        MATCH (source:Country {iso3_code: $reporter})
        MATCH (target:Country {iso3_code: $partner})
        MERGE (source)-[r:TRADE_FLOW {year: $year, sector: $sector}]->(target)
        SET r.value = $value
        """

        # Note: For large datasets, use UNWIND/batching (PERIODIC COMMIT replacement)
        with self.driver.session() as session:
            batch = []
            batch_size = 1000
            for row in flows:
                batch.append({
                    "year": row[0],
                    "reporter": row[1],
                    "partner": row[2],
                    "sector": row[3],
                    "value": row[4]
                })
                if len(batch) >= batch_size:
                    session.run(cypher, batch) # This needs unwinding in query or loop
                    # Simplified loop for prototype:
                    for item in batch:
                         session.run(cypher, **item)
                    batch = []
            
            # Process remaining
            for item in batch:
                session.run(cypher, **item)
                
        print(f"Ingested {len(flows)} trade flows.")

if __name__ == "__main__":
    # Ensure you run 'dbt run' first to populate the duckdb file
    ingestor = KnowledgeGraphIngestor(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, DUCKDB_PATH)
    try:
        ingestor.apply_schema()
        # ingestor.ingest_countries() # Uncomment when DB is ready
        # ingestor.ingest_sectors()
        # ingestor.ingest_trade_flows()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ingestor.close()
