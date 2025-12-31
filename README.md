# Panipuri: Global Economic World Twin v3.0

A high-fidelity "digital twin" of the global economy, integrating a Knowledge Graph (Neo4j) with a Julia-based Agent-Based Model (ABM).

## Structure

- **airflow/**: ETL pipelines and orchestration (@Harmo)
- **kg/**: Knowledge Graph schema and ingestion scripts (@Libby)
- **simulation/**: Julia ABM core and logic (@Jules, @Q)
- **api/**: FastAPI and GraphQL endpoints (@Archie)
- **dashboard/**: Streamlit UI and visualizations (@Viz)
- **data/**: Local data storage (mapped to Docker volumes)
- **docs/**: Project documentation and plans
- **tests/**: Test suites (@Audit)

## Getting Started

1. **Prerequisites**: Docker, Python 3.10+, Julia 1.10+
2. **Setup**:
   ```bash
   make setup
   ```
3. **Run Infrastructure**:
   ```bash
   make up
   ```

See `docs/G3_Plan_v3.md` for the detailed architectural plan.
