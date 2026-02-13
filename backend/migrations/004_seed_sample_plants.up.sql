WITH fam AS (
  INSERT INTO families (scientific_name) VALUES ('Lamiaceae')
  ON CONFLICT (scientific_name) DO UPDATE SET scientific_name = EXCLUDED.scientific_name
  RETURNING id
), gen AS (
  INSERT INTO genera (family_id, scientific_name)
  VALUES ((SELECT id FROM fam), 'Ocimum')
  ON CONFLICT (family_id, scientific_name) DO UPDATE SET scientific_name = EXCLUDED.scientific_name
  RETURNING id
), sp AS (
  INSERT INTO species (genus_id, scientific_epithet, author_citation, accepted_name)
  VALUES ((SELECT id FROM gen), 'tenuiflorum', '', TRUE)
  ON CONFLICT (genus_id, scientific_epithet, author_citation) DO UPDATE SET accepted_name = EXCLUDED.accepted_name
  RETURNING id
), p AS (
  INSERT INTO plants (species_id, scientific_name, plant_type, lifecycle, description)
  VALUES ((SELECT id FROM sp), 'Ocimum tenuiflorum', 'herb', 'perennial', 'Holy basil used in Indian households.')
  ON CONFLICT (species_id) DO UPDATE SET description = EXCLUDED.description
  RETURNING id
)
INSERT INTO plant_common_names (plant_id, language_id, region_id, common_name, is_primary)
VALUES
((SELECT id FROM p), (SELECT id FROM languages WHERE code='en'), (SELECT id FROM regions WHERE state_code='IN-KA'), 'Tulsi', TRUE),
((SELECT id FROM p), (SELECT id FROM languages WHERE code='hi'), (SELECT id FROM regions WHERE state_code='IN-UP'), 'तुलसी', FALSE)
ON CONFLICT (plant_id, language_id, region_id, common_name) DO NOTHING;

INSERT INTO plant_region_seasons (plant_id, region_id, season_id, start_month, end_month, suitability_score)
SELECT p.id, r.id, s.id, 6, 11, 84
FROM plants p
JOIN regions r ON r.state_code = 'IN-KA'
JOIN seasons s ON s.code = 'monsoon'
WHERE p.scientific_name = 'Ocimum tenuiflorum'
ON CONFLICT (plant_id, region_id, season_id, start_month, end_month) DO UPDATE SET suitability_score = EXCLUDED.suitability_score;
