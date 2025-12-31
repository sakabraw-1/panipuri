# Global Economic World Twin v3.0
**A Comprehensive Hybrid Knowledge Graph & Macro-ABM Simulation System**

## 1. Executive Summary & Vision
This project aims to develop a high-fidelity "digital twin" of the global economy, integrating a **Knowledge Graph (KG)** for structural data (supply chains, trade networks, policies) with a **Julia-based Agent-Based Model (ABM)** for dynamic simulations (shocks, policies, emergent behaviors). Building on v1.0's foundational breadth and v2.0's refined principles, v3.0 emphasizes scalability, real-time updates, and user-driven scenarios.

**Key Differentiators:**
- Solves "static data" issues via a living KG initialized from diverse sources.
- Addresses "black box" simulations by linking agents/parameters to provenance.
- Supports probabilistic harmonization for imperfect data mappings.
- Enables continuous learning via ML-enhanced calibration and scenario analysis.

**Objectives:**
- Represent the global economy with open data (WIOD, UN Comtrade, IMF, etc.).
- Simulate historical dynamics and forecast policy impacts.
- Provide open-source, reproducible tools for economists, policymakers, and researchers.
- Ensure modularity for easy extension (e.g., adding sectors, countries, or micro-agents).

**Scope:** Multi-country, multi-sector model with macro agents; focus on trade, production, and fiscal/monetary policies. Initial baseline: 2018 data for G20 economies.

---

## 2. Core Design Principles (Refined & Expanded)

1. **Graph for Structure, Arrays for Speed:**
   - **Neo4j** models topology (e.g., trade links, IO matrices).
   - **Julia Arrays/Sparse Matrices** handle dynamics (e.g., network propagation without traversals).
   - **Benefit:** Scales to thousands of nodes/edges; enables real-time queries.

2. **Hybrid Persistence Strategy (The "Log-Light" Rule):**
   - **Metadata & Aggregates** → Neo4j (queryable, versioned).
   - **High-Frequency Trajectories** → Parquet/MinIO (bulk, linked via URIs).
   - **Avoid:** Tick-level writes to graph; use buffering for efficiency.
   - **Benefit:** Balances searchability with storage costs.

3. **Probabilistic Data Harmonization:**
   - Acknowledges mismatches (e.g., HS vs. ISIC codes).
   - **Concordance Engine:** Weighted mappings (e.g., 40% Sector A, 60% Sector B).
   - **Benefit:** Handles uncertainty; improves accuracy over rigid 1:1 mappings.

4. **Modular & Extensible Architecture:**
   - Plugin-based agents/modules (e.g., add households/banks).
   - API-first design for integrations (e.g., external ML models).
   - **Benefit:** Evolves with new data/policies without full rewrites.

5. **Continuous Updating & Calibration:**
   - Scheduled ETL for data freshness.
   - ML-assisted parameter tuning against historical targets.
   - **Benefit:** Adapts to real-world changes (e.g., post-pandemic recovery).

6. **Open-Source & Reproducible:**
   - All code/data public; Docker for environment parity.
   - Provenance tracking for every data point/agent.
   - **Benefit:** Builds trust; enables community contributions.

---

## 3. Tech Stack & Tools (Detailed)

### Data Engineering & Harmonization
- **DuckDB:** High-performance SQL for local ETL; handles large CSVs/Parquets.
- **dbt:** Manages SQL transformations; ensures lineage and testing.
- **MinIO:** S3-compatible storage for raw data, logs, and artifacts.
- **Apache Arrow/Parquet:** Zero-copy data exchange between layers.

### Knowledge Graph
- **Neo4j (Community Edition):** Graph DB for world state; supports Cypher queries.
- **Neomo/Custom Python:** Schema validation and constraints.
- **RDF/OWL (Optional):** For semantic interoperability via Apache Jena.

### Simulation Core
- **Julia 1.10+:** Compute engine; JIT compilation for speed.
- **Agents.jl:** Agent management; supports heterogeneous agents.
- **Graphs.jl:** Network analysis (e.g., centrality, shortest paths).
- **DifferentialEquations.jl (Optional):** For continuous-time dynamics.
- **DrWatson.jl:** Experiment tracking and reproducibility.

### Orchestration & APIs
- **Apache Airflow:** DAGs for ETL, ingestion, and runs.
- **FastAPI:** REST APIs for triggers/queries.
- **Strawberry:** GraphQL for complex KG queries.
- **Docker DevContainers:** Ensures Julia/Python parity.

### Frontend & Analytics
- **Streamlit:** Dashboards for scenarios and results.
- **Plotly/Cytoscape.js:** Visualizations (networks, time-series).
- **ML Libraries (Python/Julia):** Scikit-learn/Flux.jl for calibration.

### DevOps & Monitoring
- **GitHub Actions:** CI/CD for testing/deployments.
- **Prometheus/Grafana:** Monitoring pipelines and simulations.
- **Makefile/Docker Compose:** Local dev setup.

**Rationale:** All open-source; balances performance (Julia) with ecosystem (Python).

---

## 4. Architecture

### 4.1 Logical Layers
```mermaid
flowchart LR
    subgraph Raw["Raw Data Layer"]
        Sources[UN Comtrade, WIOD, IMF, World Bank] --> MinIO_Raw[MinIO (Raw JSON/CSV)]
    end

    subgraph ETL["Harmonization Layer"]
        MinIO_Raw --> DuckDB
        DuckDB --> Concordance[Concordance Engine (dbt)]
        Concordance --> CleanTables[Clean Harmonized Tables]
    end

    subgraph Graph["Knowledge Graph Layer (Neo4j)"]
        CleanTables --> Ingest[KG Ingestion]
        Ingest --> Neo4j[(World Graph)]
        Neo4j --> SnapshotAPI[Snapshot API]
        Neo4j --> QueryAPI[Query API]
    end

    subgraph Sim["Simulation Layer (Julia)"]
        SnapshotAPI --> Init[WorldBuilder.jl]
        Init --> Model[SimLoop (Agents.jl)]
        Model --> BulkOutput[Parquet Logs -> MinIO]
        Model --> MetaOutput[Run Metadata -> Neo4j]
    end

    subgraph Analytics["Analytics & Control"]
        QueryAPI --> ML[ML Calibration]
        ML --> Scenarios[Scenario Manager]
        Scenarios --> Orchestrator[Run Orchestrator]
        Orchestrator --> Model
    end

    subgraph UI["User Interface"]
        QueryAPI --> Dashboard[Streamlit Dashboard]
        BulkOutput --> Dashboard
    end
```

### 4.2 The "Concordance Engine" (Expanded)
- **Responsibility:** Maps taxonomies (HS2017/2012, ISIC Rev4, NACE) to Internal_Sector_ID.
- **Logic:** Weighted tables from correspondence sources (e.g., UN/World Bank mappings). Splits values probabilistically.
- **Implementation:** dbt models for transformations; stores rules in Neo4j as ConcordanceRule nodes.
- **Example:** Steel (HS 7207) maps 70% to Manufacturing (ISIC C25), 30% to Mining (ISIC B07).

### 4.3 Data Flow
1. Raw data → ETL → Harmonized tables → KG ingestion → Snapshots.
2. Snapshots → Simulation init → Runs → Outputs → KG persistence.
3. Queries/Analytics → Dashboards.

---

## 5. Economic Knowledge Graph Design (Detailed)

### 5.1 Node Types
- **Country:** Properties: iso3_code, name, region, gdp_latest, population, currency.
- **Sector:** Properties: id, name, classification (WIOD/ISIC), country_id.
- **Commodity/Product:** Properties: hs_code, description, sector_links (array).
- **MacroVariable:** Properties: name (e.g., GDP_REAL), unit, frequency (quarterly).
- **PolicyInstrument:** Properties: type (tariff, subsidy), params (rate, target).
- **Institution:** Properties: name (WTO, IMF), type (intergov).
- **Event:** Properties: name, date, type (crisis), impact_score.
- **Dataset:** Properties: name (WIOD), version, url, last_updated.
- **RunMetadata:** Properties: scenario_id, timestamp, minio_uri, params.
- **CalibrationTarget:** Properties: fact (e.g., "US Trade/GDP 2020"), value, source.
- **ConcordanceRule:** Properties: from_taxonomy, to_taxonomy, weights.
- **SimState:** Properties: replicate, time, variable, value.

### 5.2 Edge Types
- **IO_LINK:** (Sector_i) -[:INPUT_TO {year, coeff, value}]-> (Sector_j) – Domestic IO.
- **TRADE_FLOW:** (Country_a) -[:EXPORTS {year, sector, value}]-> (Country_b) – Bilateral trade.
- **HAS_INDICATOR:** (Country) -[:VALUE {time, value}]-> (MacroVariable).
- **MEMBER_OF:** (Country) -[:MEMBER {since}]-> (Institution).
- **SUBJECT_TO:** (Country) -[:APPLIES {time, rate}]-> (PolicyInstrument).
- **AFFECTS:** (Event) -[:IMPACTS {sign, magnitude}]-> (Country/Sector).
- **DERIVED_FROM:** (Any) -[:FROM]-> (Dataset) – Provenance.
- **RELATES_TO:** (Variable_i) -[:REL {strength}]-> (Variable_j) – Discovered relations.
- **BASED_ON_SNAPSHOT:** (RunMetadata) -[:USES]-> (SimState snapshot).
- **GENERATED_FILE:** (RunMetadata) -[:LINKS_TO]-> (Artifact {url}).

### 5.3 Schema & Constraints
- Use Neo4j constraints for uniqueness (e.g., Country.iso3_code).
- Ontology via OWL for semantic queries.
- Versioning: Nodes have created_at, updated_at.

---

## 6. Simulation Architecture & Workflow (Detailed)

### 6.1 World Model (Julia/Agents.jl)
- **Structure:**
  - countries::Vector{CountryAgent}
  - sectors::Dict{Tuple{Country, Sector} => SectorAgent}
  - io_matrix::SparseMatrixCSC (technical coeffs)
  - trade_matrix::Dict (baseline flows)
  - macro_state::DataFrame (GDP, inflation, etc.)
  - policies::Dict (active instruments)

- **Agent Types:**
  - **CountryAgent:** Manages fiscal/monetary policy, aggregates (GDP, debt).
  - **SectorAgent:** Handles production, pricing, trade decisions.
  - **Optional Extensions:** HouseholdAgent (consumption), BankAgent (credit), FirmAgent (investment).

### 6.2 Time-Step Loop (Per Replicate)
For t in 1:T:
1. **Exogenous Updates:** Apply shocks/policies from scenario.
2. **Agent Decisions:**
   - Sectors: Set prices, production, input demands.
   - Countries: Adjust rates, spending.
3. **Market Clearing:** Solve for equilibria (goods, labor, FX).
4. **Network Propagation:** Update via IO/trade matrices.
5. **Aggregation/Logging:** Compute macros; buffer to Parquet.
6. **Checkpointing:** Periodic saves to MinIO.

### 6.3 Calibration & Validation
- **Process:** Run historical simulations; optimize params (e.g., via BlackBoxOptim.jl) against CalibrationTarget nodes.
- **Metrics:** RMSE on GDP growth, trade volumes.
- **ML Integration:** Use graph embeddings for feature selection.

### 6.4 Orchestration
- **DAG:** Validate → Extract Snapshot → Calibrate → Simulate → Aggregate → Persist.
- **Parallelism:** Replicates via Julia's distributed computing.

---

## 7. Revised Roadmap (Phased & Detailed)

### Phase 1: Foundation & Concordance (Weeks 1-6)
**Goal:** Robust data pipeline and KG basics.
**Deliverables:**
- MinIO/DuckDB setup; ETL for WIOD/Comtrade.
- Concordance Engine (dbt models); basic Neo4j schema.
- KG ingestion scripts; snapshot API.
**Risks:** Data source API changes; mitigation: fallback to cached data.
**Timeline:** Week 1-2: Connectors; 3-4: Harmonization; 5-6: KG ingestion.

### Phase 2: Static Twin (Weeks 7-12)
**Goal:** Queryable KG for 2018 baseline.
**Deliverables:**
- Full KG population; query API for networks/indicators.
- WorldBuilder.jl for snapshot conversion.
- Basic UI for exploration.
**Risks:** Performance bottlenecks; mitigation: Optimize Cypher queries.
**Timeline:** 7-8: Ingestion; 9-10: APIs; 11-12: UI.

### Phase 3: Dynamic Twin (Weeks 13-20)
**Goal:** Running simulations without crashes.
**Deliverables:**
- SimLoop.jl with agents; market clearing.
- Calibration suite; hybrid logging.
- Orchestrator for runs.
**Risks:** Numerical instability; mitigation: Add bounds/checks.
**Timeline:** 13-15: Agents; 16-18: Dynamics; 19-20: Calibration.

### Phase 4: Calibration & Interface (Weeks 21-28)
**Goal:** Tuned model with full UI.
**Deliverables:**
- ML calibration; scenario manager.
- Streamlit dashboard; result visualizations.
- Documentation and tests.
**Risks:** Overfitting; mitigation: Cross-validation.
**Timeline:** 21-23: Calibration; 24-26: UI; 27-28: Polish.

### Phase 5: Scaling & Extensions (Weeks 29+)
**Goal:** Real-time updates and expansions.
**Deliverables:**
- Scheduled ETL; ML enhancements.
- Add micro-agents; global extensions.
- Community docs and tutorials.
**Risks:** Resource limits; mitigation: Cloud migration.

**Overall Timeline:** 28+ weeks; iterative with feedback.

---

## 8. Development Plan (VS Code + Copilot)

### 8.1 Folder Structure
```
panipuri/
├── README.md
├── docker-compose.yml
├── Makefile
├── requirements.txt (Python)
├── Project.toml (Julia)
├── airflow/dags/ (ETL DAGs)
├── kg/ (Schema, ingestion, APIs)
├── simulation/ (Julia models)
├── api/ (FastAPI, GraphQL)
├── dashboard/ (Streamlit)
├── data/ (Raw/processed)
├── docs/ (Plans, schemas)
├── tests/ (Unit/integration)
└── scripts/ (Utilities)
```

### 8.2 Best Practices
- Use Copilot for code generation (e.g., "Implement KG ingestion from DuckDB to Neo4j").
- TDD: Write tests first.
- Version control: Git with semantic commits.
- Documentation: Inline comments; update README.

### 8.3 Resources & Budget
- **Team:** 2-3 devs (Julia/Python experts).
- **Compute:** Local Docker; scale to cloud (AWS/GCP).
- **Cost Estimate:** $5K-10K (tools, data APIs); open-source minimizes.

---

## 9. Risks, Assumptions, & Mitigation
- **Data Quality:** Incomplete sources; mitigation: Probabilistic models.
- **Scalability:** Large matrices; mitigation: Sparse ops, distributed Julia.
- **Accuracy:** Simulations approximate; mitigation: Validation against history.
- **Assumptions:** Open data suffices; policies are exogenous.

This v3.0 plan integrates v1's depth with v2's focus, providing a blueprint for a production-ready digital twin.</content>
<parameter name="filePath">c:\Prototypes\panipuri\docs\G3_Plan_v3.md