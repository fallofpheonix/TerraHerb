CREATE TABLE IF NOT EXISTS families (
  id BIGSERIAL PRIMARY KEY,
  scientific_name VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS genera (
  id BIGSERIAL PRIMARY KEY,
  family_id BIGINT NOT NULL REFERENCES families(id) ON DELETE RESTRICT,
  scientific_name VARCHAR(120) NOT NULL,
  UNIQUE (family_id, scientific_name)
);

CREATE TABLE IF NOT EXISTS species (
  id BIGSERIAL PRIMARY KEY,
  genus_id BIGINT NOT NULL REFERENCES genera(id) ON DELETE RESTRICT,
  scientific_epithet VARCHAR(120) NOT NULL,
  author_citation VARCHAR(255),
  accepted_name BOOLEAN NOT NULL DEFAULT TRUE,
  UNIQUE (genus_id, scientific_epithet, author_citation)
);

CREATE TABLE IF NOT EXISTS plants (
  id BIGSERIAL PRIMARY KEY,
  species_id BIGINT NOT NULL UNIQUE REFERENCES species(id) ON DELETE RESTRICT,
  scientific_name VARCHAR(255) NOT NULL,
  plant_type VARCHAR(20) NOT NULL CHECK (plant_type IN ('herb','crop','tree','weed','shrub','climber')),
  lifecycle VARCHAR(20) NOT NULL CHECK (lifecycle IN ('annual','biennial','perennial')),
  description TEXT,
  is_invasive BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT now(),
  updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS regions (
  id BIGSERIAL PRIMARY KEY,
  country_code CHAR(2) NOT NULL DEFAULT 'IN',
  state_code VARCHAR(10) NOT NULL UNIQUE,
  state_name VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS languages (
  id SMALLSERIAL PRIMARY KEY,
  code VARCHAR(10) NOT NULL UNIQUE,
  name VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS plant_common_names (
  id BIGSERIAL PRIMARY KEY,
  plant_id BIGINT NOT NULL REFERENCES plants(id) ON DELETE CASCADE,
  language_id SMALLINT NOT NULL REFERENCES languages(id) ON DELETE RESTRICT,
  region_id BIGINT REFERENCES regions(id) ON DELETE SET NULL,
  common_name VARCHAR(150) NOT NULL,
  is_primary BOOLEAN NOT NULL DEFAULT FALSE,
  UNIQUE (plant_id, language_id, region_id, common_name)
);

CREATE TABLE IF NOT EXISTS climate_zones (
  id BIGSERIAL PRIMARY KEY,
  code VARCHAR(30) NOT NULL UNIQUE,
  label VARCHAR(120) NOT NULL
);

CREATE TABLE IF NOT EXISTS region_climate_zones (
  region_id BIGINT NOT NULL REFERENCES regions(id) ON DELETE CASCADE,
  climate_zone_id BIGINT NOT NULL REFERENCES climate_zones(id) ON DELETE RESTRICT,
  PRIMARY KEY (region_id, climate_zone_id)
);

CREATE TABLE IF NOT EXISTS seasons (
  id SMALLSERIAL PRIMARY KEY,
  code VARCHAR(20) NOT NULL UNIQUE,
  label VARCHAR(80) NOT NULL
);

CREATE TABLE IF NOT EXISTS plant_region_seasons (
  id BIGSERIAL PRIMARY KEY,
  plant_id BIGINT NOT NULL REFERENCES plants(id) ON DELETE CASCADE,
  region_id BIGINT NOT NULL REFERENCES regions(id) ON DELETE CASCADE,
  season_id SMALLINT NOT NULL REFERENCES seasons(id) ON DELETE RESTRICT,
  start_month SMALLINT NOT NULL CHECK (start_month BETWEEN 1 AND 12),
  end_month SMALLINT NOT NULL CHECK (end_month BETWEEN 1 AND 12),
  suitability_score NUMERIC(5,2) CHECK (suitability_score BETWEEN 0 AND 100),
  UNIQUE (plant_id, region_id, season_id, start_month, end_month)
);

CREATE TABLE IF NOT EXISTS soil_types (
  id SMALLSERIAL PRIMARY KEY,
  code VARCHAR(30) NOT NULL UNIQUE,
  label VARCHAR(120) NOT NULL
);

CREATE TABLE IF NOT EXISTS water_requirements (
  id SMALLSERIAL PRIMARY KEY,
  level VARCHAR(20) NOT NULL UNIQUE CHECK (level IN ('low','medium','high'))
);

CREATE TABLE IF NOT EXISTS plant_soil_preferences (
  plant_id BIGINT NOT NULL REFERENCES plants(id) ON DELETE CASCADE,
  soil_type_id SMALLINT NOT NULL REFERENCES soil_types(id) ON DELETE RESTRICT,
  preference_rank SMALLINT NOT NULL CHECK (preference_rank BETWEEN 1 AND 5),
  PRIMARY KEY (plant_id, soil_type_id)
);

CREATE TABLE IF NOT EXISTS plant_water_requirements (
  plant_id BIGINT PRIMARY KEY REFERENCES plants(id) ON DELETE CASCADE,
  water_requirement_id SMALLINT NOT NULL REFERENCES water_requirements(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS medicinal_properties (
  id BIGSERIAL PRIMARY KEY,
  code VARCHAR(80) NOT NULL UNIQUE,
  label VARCHAR(120) NOT NULL
);

CREATE TABLE IF NOT EXISTS plant_medicinal_uses (
  plant_id BIGINT NOT NULL REFERENCES plants(id) ON DELETE CASCADE,
  medicinal_property_id BIGINT NOT NULL REFERENCES medicinal_properties(id) ON DELETE RESTRICT,
  part_used VARCHAR(80),
  preparation VARCHAR(120),
  evidence_level VARCHAR(20) CHECK (evidence_level IN ('traditional','preclinical','clinical')),
  PRIMARY KEY (plant_id, medicinal_property_id, part_used)
);

CREATE TABLE IF NOT EXISTS toxicity_profiles (
  id BIGSERIAL PRIMARY KEY,
  toxicity_class VARCHAR(20) NOT NULL CHECK (toxicity_class IN ('none','mild','moderate','severe')),
  warning TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plant_toxicity (
  plant_id BIGINT PRIMARY KEY REFERENCES plants(id) ON DELETE CASCADE,
  toxicity_profile_id BIGINT NOT NULL REFERENCES toxicity_profiles(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS ecological_roles (
  id SMALLSERIAL PRIMARY KEY,
  code VARCHAR(40) NOT NULL UNIQUE,
  label VARCHAR(120) NOT NULL
);

CREATE TABLE IF NOT EXISTS plant_ecological_roles (
  plant_id BIGINT NOT NULL REFERENCES plants(id) ON DELETE CASCADE,
  ecological_role_id SMALLINT NOT NULL REFERENCES ecological_roles(id) ON DELETE RESTRICT,
  PRIMARY KEY (plant_id, ecological_role_id)
);
