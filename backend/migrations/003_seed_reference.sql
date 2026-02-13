INSERT INTO languages (code, name) VALUES
('en', 'English'),
('hi', 'Hindi')
ON CONFLICT (code) DO NOTHING;

INSERT INTO seasons (code, label) VALUES
('spring', 'Spring'),
('summer', 'Summer'),
('monsoon', 'Monsoon'),
('autumn', 'Autumn'),
('winter', 'Winter'),
('year_round', 'Year Round'),
('kharif', 'Kharif'),
('rabi', 'Rabi'),
('zaid', 'Zaid')
ON CONFLICT (code) DO NOTHING;

INSERT INTO climate_zones (code, label) VALUES
('tropical_wet', 'Tropical Wet'),
('semi_arid', 'Semi Arid'),
('humid_subtropical', 'Humid Subtropical'),
('montane', 'Montane')
ON CONFLICT (code) DO NOTHING;

INSERT INTO soil_types (code, label) VALUES
('loamy', 'Loamy'),
('alluvial', 'Alluvial'),
('clayey', 'Clayey'),
('sandy', 'Sandy')
ON CONFLICT (code) DO NOTHING;

INSERT INTO water_requirements (level) VALUES
('low'), ('medium'), ('high')
ON CONFLICT (level) DO NOTHING;

INSERT INTO ecological_roles (code, label) VALUES
('pollinator_support', 'Pollinator Support'),
('soil_binding', 'Soil Binding')
ON CONFLICT (code) DO NOTHING;

INSERT INTO medicinal_properties (code, label) VALUES
('anti_inflammatory', 'Anti-inflammatory'),
('digestive_support', 'Digestive Support')
ON CONFLICT (code) DO NOTHING;

INSERT INTO toxicity_profiles (toxicity_class, warning) VALUES
('none', 'No major toxicity in normal use'),
('mild', 'Use with caution in high doses')
ON CONFLICT DO NOTHING;

INSERT INTO regions (state_code, state_name) VALUES
('IN-KA', 'Karnataka'),
('IN-MH', 'Maharashtra'),
('IN-TN', 'Tamil Nadu'),
('IN-UP', 'Uttar Pradesh')
ON CONFLICT (state_code) DO NOTHING;
