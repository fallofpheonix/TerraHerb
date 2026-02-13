CREATE INDEX IF NOT EXISTS idx_plants_type_lifecycle ON plants(plant_type, lifecycle);
CREATE INDEX IF NOT EXISTS idx_plants_scientific_name ON plants(scientific_name);
CREATE INDEX IF NOT EXISTS idx_plant_names_name ON plant_common_names(common_name);
CREATE INDEX IF NOT EXISTS idx_plant_names_lang_region ON plant_common_names(language_id, region_id);
CREATE INDEX IF NOT EXISTS idx_prs_region_month ON plant_region_seasons(region_id, start_month, end_month);
CREATE INDEX IF NOT EXISTS idx_prs_plant_region ON plant_region_seasons(plant_id, region_id);
CREATE INDEX IF NOT EXISTS idx_region_climate_zone ON region_climate_zones(climate_zone_id, region_id);
CREATE INDEX IF NOT EXISTS idx_psp_soil ON plant_soil_preferences(soil_type_id, plant_id);
CREATE INDEX IF NOT EXISTS idx_pmu_property ON plant_medicinal_uses(medicinal_property_id, plant_id);
