# Global Economic World Twin v2.0
**A Hybrid Knowledge Graph & Macro-ABM Simulation System**

## 1. Executive Summary & Vision
This project aims to build a high-fidelity "digital twin" of the global economy. Unlike standard econometric models, this system couples a **Knowledge Graph (KG)** (representing the structural reality of supply chains, trade treaties, and ownership) with a **Julia-based Agent-Based Model (ABM)** (simulating flow dynamics, shocks, and emergent behavior).

**Key Differentiator:** The system solves the "static data" problem by using the KG as a living initial condition for simulations, and solves the "black box" simulation problem by linking every agent and parameter back to real-world provenance.

---

## 2. Core Design Principles (Refined)

1.  **Graph for Structure, Arrays for Speed:**
    * Use **Neo4j** to model *topology* (Who trades with whom? Which sector relies on which input?).
    * Use **Julia/Arrays** for *dynamics* (Compute interactions using sparse matrices and vector operations, not graph traversals).

2.  **Hybrid Persistence Strategy (The "Log-Light" Rule):**
    * **Metadata & Aggregate Results** $\rightarrow$ Neo4j (Searchable, queryable).
    * **High-Frequency Trajectories** $\rightarrow$ Parquet/MinIO (Bulk storage, accessible via link).
    * *Avoid writing millions of tick-level simulation updates into the Graph.*

3.  **Probabilistic Data Harmonization:**
    * Acknowledge that trade data (HS Codes) and production data (ISIC/NACE) never map 1:1.
    * Implement a dedicated **Concordance Engine** that handles these mappings explicitly.

---

## 3. Tech Stack & Tools

### Data Engineering & Concordance
* **DuckDB:** Local high-performance SQL engine for initial data cleaning.
* **dbt (Data Build Tool):** For managing the SQL transformations and lineage of the harmonization process.
* **MinIO:** Object storage for raw artifacts and simulation logs (Parquet).

### Knowledge Graph
* **Neo4j:** Stores the "World State" snapshots and provenance.
* **Neomo (or custom Python scripts):** For schema enforcement and constraints.

### Simulation Core
* **Julia 1.10+:** The compute engine.
* **Agents.jl:** For agent management.
* **Graphs.jl:** For optimized network analysis within the simulation.
* **Arrow.jl / Parquet.jl:** For zero-copy data exchange with the storage layer.

### Orchestration & API
* **Apache Airflow:** Pipeline orchestration.
* **FastAPI:** Backend for triggering runs and querying results.
* **Docker DevContainers:** To ensure Julia/Python environment parity across dev teams.

---

## 4. Architecture

### 4.1 Logical Layers

```mermaid
flowchart LR
    subgraph Raw["Raw Data Layer"]
        Sources[UN Comtrade, WIOD, IMF] --> MinIO_Raw[MinIO (Raw JSON/CSV)]
    end

    subgraph ETL["Harmonization Layer"]
        MinIO_Raw --> DuckDB
        DuckDB --> Concordance[Concordance Engine (dbt)]
        Concordance --> CleanTables[Clean Harmonized Tables]
    end

    subgraph Graph["Knowledge Layer (Neo4j)"]
        CleanTables --> Ingest[KG Ingestion]
        Ingest --> Neo4j[(World Graph)]
        Neo4j --> SnapshotAPI[Snapshot API]
    end

    subgraph Sim["Simulation Layer (Julia)"]
        SnapshotAPI --> Init[WorldBuilder.jl]
        Init --> Model[SimLoop (Agents.jl)]
        Model --> BulkOutput[Parquet Logs -> MinIO]
        Model --> MetaOutput[Run Metadata -> Neo4j]
    end

## 4.2 The "Concordance Engine" (New Component)

**Responsibility:** Maps diverse taxonomies (HS2017, HS2012, ISIC Rev4, NACE) to a unified Internal_Sector_ID.

**Logic:** Uses weighted correspondence tables (e.g., if Product X maps to Sector A (40%) and Sector B (60%), the engine splits the value accordingly during ingestion).

---

# 5. Economic Knowledge Graph Design

## 5.1 Updated Nodes

- **RunMetadata:** Stores parameters, timestamp, and a URI pointer to the full results in MinIO.
- **CalibrationTarget:** A node representing a "stylized fact" (e.g., "Trade-to-GDP Ratio, USA, 2020") used to validate runs.
- **ConcordanceRule:** Stores the logic used to map disparate data sources (provenance for data cleaning).

## 5.2 Updated Edges

- `(:RunMetadata)-[:BASED_ON_SNAPSHOT]->(:SimState)`: Ensures reproducibility.
- `(:RunMetadata)-[:GENERATED_FILE]->(:Artifact {url: "s3://..."})`: The link to bulk data.

---

# 6. Simulation Workflow (The "Replicate" Loop)

- **Scenario Definition:** User defines a shock (e.g., "Increase Tariff on Steel by 20%").
- **Snapshot Loading:** Julia pulls the relevant world state (countries, trade matrix) from Neo4j.
- **Execution (Julia):**
  - Time Step $t=1 \dots T$
  - Agents (Sectors) adjust prices/production.
  - Agents (Nations) adjust rates/spending.
  - Flux: Trade flows update based on relative prices and gravity model.
- **Logging:**
  - Heavy Data: Position/State of every agent at every step $\rightarrow$ Buffer $\rightarrow$ Parquet File.
  - Light Data: Aggregate GDP, Total Trade Volume $\rightarrow$ Memory.
- **Finalization:**
  - Upload Parquet file to MinIO.
  - Create RunMetadata node in Neo4j with aggregate stats and link to Parquet.

---

# 7. Revised Roadmap

## Phase 1: Foundation & Concordance (Weeks 1-4)

**Goal:** A working data pipeline that can ingest WIOD and Comtrade and handle code mismatches.

**Deliverables:**
- MinIO + DuckDB setup.
- Concordance Engine: Scripts to map HS codes to WIOD sectors.
- Basic Neo4j schema design.

## Phase 2: The Static Twin (Weeks 5-8)

**Goal:** A traversable graph of the world economy for a single base year (e.g., 2018).

**Deliverables:**
- Ingestion scripts (DuckDB $\rightarrow$ Neo4j).
- API to query: "Who supplies inputs to German Auto Makers?"

## Phase 3: The Dynamic Twin (Weeks 9-14)

**Goal:** A Julia simulation that can initialize from the Graph and run without crashing.

**Deliverables:**
- WorldBuilder.jl: Converter from Graph Snapshot to Agents.jl model.
- Basic Market Clearing mechanism.
- Hybrid Logging (Parquet + Graph).

## Phase 4: Calibration & Interface (Weeks 15+)

**Goal:** Tuning the model to match history and building the UI.

**Deliverables:**
- Calibration suite (running simulations against historical CalibrationTarget nodes).
- Streamlit Dashboard (reading Graph for metadata and MinIO for time-series plots).