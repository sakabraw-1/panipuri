// Constraints
CREATE CONSTRAINT country_iso3_unique IF NOT EXISTS FOR (c:Country) REQUIRE c.iso3_code IS UNIQUE;
CREATE CONSTRAINT sector_id_unique IF NOT EXISTS FOR (s:Sector) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT run_metadata_id_unique IF NOT EXISTS FOR (r:RunMetadata) REQUIRE r.scenario_id IS UNIQUE;
CREATE CONSTRAINT commodity_hs_unique IF NOT EXISTS FOR (p:Commodity) REQUIRE p.hs_code IS UNIQUE;

// Indexes
CREATE INDEX country_name_index IF NOT EXISTS FOR (c:Country) ON (c.name);
CREATE INDEX sector_name_index IF NOT EXISTS FOR (s:Sector) ON (s.name);
CREATE INDEX trade_flow_year_index IF NOT EXISTS FOR ()-[r:TRADE_FLOW]-() ON (r.year);
