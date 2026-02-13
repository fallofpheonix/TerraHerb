package models

type Plant struct {
	ID                int64    `json:"id"`
	ScientificName    string   `json:"scientific_name"`
	PrimaryCommonName string   `json:"primary_common_name"`
	PlantType         string   `json:"plant_type"`
	Lifecycle         string   `json:"lifecycle"`
	InSeason          bool     `json:"in_season"`
	SuitabilityScore  float64  `json:"suitability_score"`
	ClimateZones      []string `json:"climate_zones"`
}

type PlantDetail struct {
	ID                int64            `json:"id"`
	ScientificName    string           `json:"scientific_name"`
	PlantType         string           `json:"plant_type"`
	Lifecycle         string           `json:"lifecycle"`
	Description       string           `json:"description,omitempty"`
	CommonNames       []LocalizedName  `json:"common_names"`
	Taxonomy          Taxonomy         `json:"taxonomy"`
	SoilPreferences   []string         `json:"soil_preferences"`
	WaterRequirement  string           `json:"water_requirement"`
	Seasonality       []SeasonalWindow `json:"seasonality"`
	MedicinalUses     []MedicinalUse   `json:"medicinal_uses"`
	Toxicity          Toxicity         `json:"toxicity"`
	EcologicalRoles   []string         `json:"ecological_roles"`
	IsInvasive        bool             `json:"is_invasive"`
}

type LocalizedName struct {
	Name       string  `json:"name"`
	Language   string  `json:"language"`
	RegionCode *string `json:"region_code"`
}

type Taxonomy struct {
	Family  string `json:"family"`
	Genus   string `json:"genus"`
	Species string `json:"species"`
}

type SeasonalWindow struct {
	RegionCode       string  `json:"region_code"`
	Season           string  `json:"season"`
	StartMonth       int     `json:"start_month"`
	EndMonth         int     `json:"end_month"`
	SuitabilityScore float64 `json:"suitability_score"`
}

type MedicinalUse struct {
	Property      string `json:"property"`
	PartUsed      string `json:"part_used,omitempty"`
	Preparation   string `json:"preparation,omitempty"`
	EvidenceLevel string `json:"evidence_level,omitempty"`
}

type Toxicity struct {
	Class   string `json:"toxicity_class"`
	Warning string `json:"warning"`
}

type PlantSearchParams struct {
	Query       string
	Season      string
	ClimateZone string
	RegionCode  string
	Month       int
	PlantType   string
	Lifecycle   string
	Page        int
	Limit       int
}
