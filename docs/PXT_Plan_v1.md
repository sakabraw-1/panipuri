Global Economic World Twin
A Knowledge Graph + Simulation System for the Real World

This document describes the end‑to‑end design of a global economic “world twin” that combines: (1) a rich economic knowledge graph, and (2) a high‑fidelity macro/agent‑based simulation engine, built with an open‑source tech stack and developed in Visual Studio Code with Copilot. The goal is to simulate the existing world in a way that is high‑level but extremely detailed and realistic.
​

1. Goals and Design Principles
Represent the real global economy (countries, sectors, trade, macro variables, policies, events) with as much detail as open data allows.
​

Maintain a knowledge graph (KG) as the canonical world state, integrating WIOD/IO tables, UN Comtrade, Global Macro Database, World Bank, and other public sources.
​

Build a macro / agent‑based simulation engine that:

Initializes from the KG,

Reproduces historical dynamics reasonably well,

Supports realistic policy and shock experiments.
​

Keep everything as open‑source as possible: databases, frameworks, libraries, toolchain.

Support continuous updating: scheduled data ingestion, KG enrichment, and periodic re‑calibration.
​

2. Tech Stack (Open Source)
Data & Storage

DuckDB – local analytical database for harmonized tables.

MinIO – S3‑compatible object storage for raw data and simulation artifacts.

Optional: Postgres for metadata.

Orchestration

Apache Airflow – ETL and data pipeline orchestration.
​

Knowledge Graph

Neo4j Community Edition – graph database for the economic KG.

RDF/OWL compatible schema if needed via Apache Jena or similar.
​

Simulation Engine

Julia 1.10+

Agents.jl (or similar) – high‑performance agent‑based modeling framework.
​

DataFrames.jl, CSV.jl, JSON3.jl – data I/O.

DrWatson.jl – experiment tracking.
​

Backend APIs

Python 3.11+

FastAPI – REST APIs.

Strawberry – GraphQL schema.

Frontend & Visualization

Streamlit – dashboards and scenario UI.

Plotly / Cytoscape.js – network and time‑series visualizations.

Dev & Ops

Docker / Docker Compose – local multi‑service dev.

GitHub Actions – CI/CD.

VS Code + GitHub Copilot – coding agent.

3. High‑Level Architecture
3.1 Logical Architecture
Data & ETL Layer

Fetches raw economic data from official APIs and files (UN Comtrade, WIOD/IO, GMD, WDI, IMF).
​

Harmonizes codes, units, and time; reconciles trade and IO discrepancies.
​

Stores clean tables in DuckDB and raw files in MinIO.

Knowledge Graph Layer

Neo4j graph representing countries, sectors, commodities, IO and trade networks, macro indicators, policies, events, and provenance.
​

Exposes APIs to get world snapshots, networks, and calibration targets.

Simulation Layer

Julia‑based macro/ABM: countries and sectors interacting via IO and trade networks, plus macro agents (households, banks, governments, central banks).
​

Uses KG to initialize and to calibrate; writes simulated states back into the KG.

Analytics & Control Layer

ML and macro‑KG analytics for forecasting and variable selection.
​

Scenario manager, run orchestration, and dashboards.

3.2 Mermaid Architecture Diagram
text
flowchart LR

  subgraph Data_ETL["Data & ETL Layer"]
    A1[UN Comtrade API] -->|raw trade| E1[ETL Jobs]
    A2[WIOD / IO Tables] -->|IO matrices| E1
    A3[Global Macro DB] -->|macro time series| E1
    A4[World Bank / IMF] -->|indicators| E1
    E1 --> D1[DuckDB (harmonized)]
    E1 --> S3[MinIO (raw)]
  end

  subgraph KG["Knowledge Graph Layer (Neo4j)"]
    D1 --> K1[KG Ingestion Service]
    K1 --> NEO[(Neo4j)]
    NEO --> KAPI[KG Query API]
  end

  subgraph Sim["Simulation Layer (Julia)"]
    KAPI --> J1[Init Service]
    J1 --> J2[WorldModel (Agents.jl)]
    J2 --> J3[Calibration Service]
    J2 --> J4[Simulation Runs]
    J4 --> KAPI
  end

  subgraph API["Backend & Control"]
    KAPI --> B1[FastAPI + GraphQL]
    B1 --> UI[Streamlit Dashboard]
    B1 --> Orchestrator[Run Orchestrator]
    Orchestrator --> J4
  end

  subgraph Orchestration["Airflow / CI"]
    AF[Airflow] --> E1
    AF --> K1
    AF --> Orchestrator
  end
4. Economic Knowledge Graph Design
4.1 Key Entities (Nodes)
Country

code (ISO3), name, region, optional aggregates (latest GDP, population).
​

Sector

id, name, classification (e.g. WIOD code), country or global sector reference.
​

Commodity / Product

hs_code, sitc_code, description, optional link to Sector.
​

MacroVariable

name (e.g. GDP_REAL, CPI, TRADE_GDP), unit, frequency.
​

PolicyInstrument

policy_id, type (tariff, VAT, subsidy, rate, sanction, carbon price), description.

Institution

name (IMF, WTO, EU, ECB, etc.).

Event

name, date, type (crisis, war, pandemic, agreement), description.

Dataset

name (WIOD, GMD, WDI, Comtrade), version, url.
​

SimState

scenario_id, country, sector (optional), variable, time, replicate.

4.2 Key Relationships (Edges)
IO_LINK(Sector_i) -[:INPUT_TO {year, coefficient, value}]-> Sector_j

Domestic IO coefficients and values.
​

TRADE_FLOW(Country_a) -[:EXPORTS {year, commodity/sector, value, quantity, source}]-> Country_b

Bilateral trade flows, aggregated or product‑level.
​

HAS_INDICATOR(Country) -[:VALUE {time, value, unit, vintage, source}]-> MacroVariable

Macro time series from GMD/WDI.
​

MEMBER_OF(Country) -[:MEMBER {since, until}]-> Institution

SUBJECT_TO(Country) -[:APPLIES {time, rate, params}]-> PolicyInstrument

OBSERVED_EVENT_AFFECTS(Event) -[:AFFECTS {sign, notes}]-> Country/Sector/Variable

DERIVED_FROM(any node) -[:FROM]-> Dataset

Provenance link to source dataset and ETL pipeline.
​

RELATES_TO(Variable_i) -[:REL {sign, strength, evidence}]-> Variable_j

Relations discovered from macro‑KG text mining and statistical validation.
​

5. Simulation Architecture and Workflow
5.1 World Model (Julia / Agents.jl)
Core structure (conceptually):

WorldModel

countries::Vector{CountryAgent}

sector_agents::Dict{(country, sector) => SectorAgent}

io_matrix::SparseMatrixCSC{Float64} (sector‑by‑sector technical coefficients).
​

trade_matrix::Dict{(from, to, sector) => Float64} (baseline trade shares/flows).
​

macro_state::DataFrame (GDP, CPI, rates, etc.).

Agent types:

CountryAgent – tracks macro variables, fiscal/monetary policy rules, financial balances.
​

SectorAgent – production, pricing, input use, exports/imports constrained by IO/trade networks.
​

Optional: households, banks, firms for more micro detail.
​

5.2 Time‑Step Loop (Per Replicate)
For each period 
t
t (e.g. quarter or year):

Exogenous Updates

Technology growth, demographics, and exogenous policy paths from KG snapshot / scenario.

Agent Decisions

Sector agents: set production, input demands, wage offers, prices; decide investment.
​

Households (if modeled): supply labor, consume, save.

Banks: extend credit, manage capital and liquidity.

Governments: tax/spend, issue debt.

Central banks: set interest/exchange rates via policy rules.

Market Clearing / Adjustment

Goods, labor, credit, FX markets adjust; if markets do not clear exactly, apply out‑of‑equilibrium adjustment.
​

Network Propagation

IO matrix and trade matrix propagate shocks through the production and trade network.
​

Aggregation & Logging

Aggregate to macro variables and trade aggregates; store per‑period statistics.

Checkpointing

Periodic state checkpoints to MinIO for restart and sensitivity analysis.

6. Simulation Sequencing and Orchestration
6.1 Run Lifecycle
Run Trigger

User or scheduler calls API with scenario_id, kg_snapshot_date, time_horizon, replicates, calibration_mode.

Input Validation

Scenario manager verifies that:

Scenario exists and references valid policies/shocks.

Requested snapshot exists in KG.

KG Snapshot Extraction

World snapshot endpoint returns:

Country list and attributes.

Sector definitions.

IO and trade networks for base year(s).
​

Macro variables and policy parameters for initialization.
​

Initialization

Julia initialization code converts this snapshot to a WorldModel instance and agent structures.
​

Calibration (optional)

Short runs over historical period to adjust behavioral parameters to match selected targets (e.g. GDP growth, trade shares, sectoral structure).
​

Calibration results are logged and linked to scenario + snapshot.

Main Simulation

Orchestrator runs multiple replicates in parallel; each replicate executes the time‑step loop for the specified horizon.
​

Post‑Processing and Validation

Aggregate across replicates to produce mean and distribution of outputs.

Compare simulated aggregates with KG time series for overlapping periods.
​

Persist to KG

Write SimState nodes and HAS_SIM_INDICATOR edges that mirror observed HAS_INDICATOR structure.

Link each run to:

Scenario node,

KG_Snapshot node,

WorldModelVersion node (code/data versions).

Result Access

APIs and dashboards can query simulated vs observed trajectories, network measures, and scenario differences.

6.2 Orchestration DAG (Conceptual)
Validate scenario → 2. Extract KG snapshot → 3. Optional calibration → 4. Launch simulation jobs → 5. Aggregate & validate → 6. Persist to KG → 7. Notify user.

Agent‑based simulation orchestration can follow standard patterns from high‑performance ABM workflows.
​

7. Major System Components and Responsibilities
7.1 Data & ETL Layer
Source Connectors

UN Comtrade: fetch bilateral trade by product/partner/time using official API.
​

WIOD / IO tables: download and parse global IO matrices.
​

Global Macro Database: load harmonized macro panel.
​

World Bank / IMF: fetch GDP, trade, debt, etc. via indicator APIs.
​

Harmonization & Transformation Service

Uniform country, sector, and product codes.

Unit and currency conversions; price base standardization.
​

Reconciliation of mirror trade flows using documented rules and adjustments.
​

Orchestration / Scheduling

Airflow DAGs that run ETL pipelines on schedules appropriate to each source (daily/weekly/monthly/annual).
​

7.2 Knowledge Graph Layer
Graph Store (Neo4j)

Persist all economic entities and relationships with temporal and provenance attributes.
​

Schema & Ontology Manager

Maintain the economic ontology: allowed node/edge types, constraints, and evolution strategy.
​

KG Ingestion Service

Transform harmonized tables into graph batches and upsert into Neo4j, preserving history and vintages.

KG Query API

Provide structured endpoints to fetch:

World snapshots,

IO/trade networks,

Macro series and calibration targets,

Scenario configuration objects.

7.3 Simulation Layer
WorldModel / Engine

Implement macro‑ABM dynamics, supporting multi‑country, multi‑sector, open economy behavior.
​

Initialization & Configuration Service

Build simulation state from KG snapshots and scenario overrides.

Calibration & Validation Service

Compare simulation outcomes with historical KG data; adjust parameters via ABM calibration methods.
​

Simulation–KG Sync Service

Persist simulation outputs to KG and maintain metadata for reproducibility.

7.4 Analytics, ML, and Control
Macro‑KG Analytics & ML

Build and maintain a macro‑knowledge graph of relations among variables using text + data; compute graph‑based features.
​

Use these to help choose variables and rules in the simulation.

Scenario Manager

Create, version, and store scenarios with policy changes, shocks, and modeling assumptions.

APIs & Dashboards

Surface data and simulations through REST/GraphQL APIs and a Streamlit UI with network and time‑series visualizations.

Monitoring & Governance

Track data freshness, pipeline health, KG consistency, simulation stability, and maintain documentation of assumptions.
​

8. Development Plan (VS Code + Copilot)
8.1 Folder Structure
text
economic-world-twin/
├── README.md
├── docker-compose.yml
├── Makefile
├── requirements.txt           # Python deps
├── Project.toml              # Julia deps
├── airflow/                  # ETL DAGs
├── kg/                       # KG schema, ingestion, query API
├── simulation/               # Julia ABM engine
├── api/                      # FastAPI + GraphQL orchestrator
├── dashboard/                # Streamlit UI
├── data/                     # raw/processed data (local)
├── docs/                     # design docs
└── tests/                    # unit/integration tests
8.2 Phased Timeline (Approximate)
Weeks 1–2:

Repo skeleton, Docker Compose, local Neo4j/Airflow/DuckDB.

Weeks 3–4:

ETL connectors for WIOD, Comtrade, GMD, WDI; pipeline to DuckDB.
​

Weeks 5–6:

KG schema, ingestion, and query API; initial world snapshot for a few major economies.
​

Weeks 7–10:

Julia WorldModel, IO/trade network integration, basic macro/ABM dynamics; initial calibration against handful of countries.
​

Weeks 11–12:

Orchestration: scenario manager, run pipeline, result persistence to KG.

Week 13:

Dashboards: world explorer, scenario builder, simulation monitor, actual vs simulated comparison.

Week 14+:

Performance tuning, deeper calibration, adding more countries/sectors and policy modules.

Copilot can be guided with focused prompts for each file/module: “Implement KG ingestion from DuckDB to Neo4j according to this schema…”, “Implement Julia WorldModel type with IO and trade networks…”, etc., using this document as the specification.