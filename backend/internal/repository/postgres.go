package repository

import (
	"context"
	"fmt"
	"strings"

	"github.com/jackc/pgx/v5/pgxpool"
	"terraherbarium/backend/internal/models"
)

type PlantRepository struct {
	pool *pgxpool.Pool
}

func NewPool(ctx context.Context, dbURL string) (*pgxpool.Pool, error) {
	return pgxpool.New(ctx, dbURL)
}

func NewPlantRepository(pool *pgxpool.Pool) *PlantRepository {
	return &PlantRepository{pool: pool}
}

func (r *PlantRepository) SearchPlants(ctx context.Context, params models.PlantSearchParams) ([]models.Plant, int, error) {
	if params.Page <= 0 {
		params.Page = 1
	}
	if params.Limit <= 0 || params.Limit > 100 {
		params.Limit = 20
	}
	offset := (params.Page - 1) * params.Limit

	var where []string
	args := []any{}
	argN := 1

	if params.Query != "" {
		where = append(where, fmt.Sprintf("(p.scientific_name ILIKE $%d OR EXISTS (SELECT 1 FROM plant_common_names pcn WHERE pcn.plant_id=p.id AND pcn.common_name ILIKE $%d))", argN, argN))
		args = append(args, "%"+params.Query+"%")
		argN++
	}
	if params.PlantType != "" {
		where = append(where, fmt.Sprintf("p.plant_type = $%d", argN))
		args = append(args, params.PlantType)
		argN++
	}
	if params.Lifecycle != "" {
		where = append(where, fmt.Sprintf("p.lifecycle = $%d", argN))
		args = append(args, params.Lifecycle)
		argN++
	}
	if params.ClimateZone != "" {
		where = append(where, fmt.Sprintf("EXISTS (SELECT 1 FROM region_climate_zones rcz JOIN climate_zones cz ON cz.id = rcz.climate_zone_id WHERE rcz.region_id = prs.region_id AND cz.code = $%d)", argN))
		args = append(args, params.ClimateZone)
		argN++
	}
	if params.Season != "" {
		where = append(where, fmt.Sprintf("s.code = $%d", argN))
		args = append(args, params.Season)
		argN++
	}
	if params.RegionCode != "" {
		where = append(where, fmt.Sprintf("r.state_code = $%d", argN))
		args = append(args, params.RegionCode)
		argN++
	}
	if params.Month > 0 {
		where = append(where, fmt.Sprintf("((prs.start_month <= prs.end_month AND $%d BETWEEN prs.start_month AND prs.end_month) OR (prs.start_month > prs.end_month AND ($%d >= prs.start_month OR $%d <= prs.end_month)))", argN, argN, argN))
		args = append(args, params.Month)
		argN++
	}

	whereSQL := ""
	if len(where) > 0 {
		whereSQL = " WHERE " + strings.Join(where, " AND ")
	}

	countSQL := "SELECT COUNT(DISTINCT p.id) FROM plants p LEFT JOIN plant_region_seasons prs ON prs.plant_id = p.id LEFT JOIN seasons s ON s.id = prs.season_id LEFT JOIN regions r ON r.id = prs.region_id" + whereSQL
	var total int
	if err := r.pool.QueryRow(ctx, countSQL, args...).Scan(&total); err != nil {
		return nil, 0, err
	}

	query := `
		SELECT DISTINCT p.id, p.scientific_name,
			COALESCE((SELECT pcn.common_name FROM plant_common_names pcn WHERE pcn.plant_id = p.id ORDER BY pcn.is_primary DESC LIMIT 1), p.scientific_name) AS common_name,
			p.plant_type, p.lifecycle,
			COALESCE(prs.suitability_score, 50) AS suitability_score
		FROM plants p
		LEFT JOIN plant_region_seasons prs ON prs.plant_id = p.id
		LEFT JOIN seasons s ON s.id = prs.season_id
		LEFT JOIN regions r ON r.id = prs.region_id
	` + whereSQL + `
		ORDER BY suitability_score DESC, p.scientific_name ASC
		LIMIT $` + fmt.Sprintf("%d", argN) + ` OFFSET $` + fmt.Sprintf("%d", argN+1)

	args = append(args, params.Limit, offset)

	rows, err := r.pool.Query(ctx, query, args...)
	if err != nil {
		return nil, 0, err
	}
	defer rows.Close()

	plants := make([]models.Plant, 0, params.Limit)
	for rows.Next() {
		var p models.Plant
		if err := rows.Scan(&p.ID, &p.ScientificName, &p.PrimaryCommonName, &p.PlantType, &p.Lifecycle, &p.SuitabilityScore); err != nil {
			return nil, 0, err
		}
		p.InSeason = p.SuitabilityScore >= 50
		plants = append(plants, p)
	}

	return plants, total, rows.Err()
}

func (r *PlantRepository) GetPlantByID(ctx context.Context, plantID int64) (*models.PlantDetail, error) {
	const query = `
		SELECT p.id, p.scientific_name, p.plant_type, p.lifecycle, COALESCE(p.description, ''), p.is_invasive,
		       f.scientific_name, g.scientific_name, sp.scientific_epithet,
		       COALESCE(wr.level, 'medium'),
		       COALESCE(tp.toxicity_class, 'none'), COALESCE(tp.warning, 'No warning available')
		FROM plants p
		JOIN species sp ON sp.id = p.species_id
		JOIN genera g ON g.id = sp.genus_id
		JOIN families f ON f.id = g.family_id
		LEFT JOIN plant_water_requirements pwr ON pwr.plant_id = p.id
		LEFT JOIN water_requirements wr ON wr.id = pwr.water_requirement_id
		LEFT JOIN plant_toxicity pt ON pt.plant_id = p.id
		LEFT JOIN toxicity_profiles tp ON tp.id = pt.toxicity_profile_id
		WHERE p.id = $1
	`

	var d models.PlantDetail
	if err := r.pool.QueryRow(ctx, query, plantID).Scan(
		&d.ID, &d.ScientificName, &d.PlantType, &d.Lifecycle, &d.Description, &d.IsInvasive,
		&d.Taxonomy.Family, &d.Taxonomy.Genus, &d.Taxonomy.Species,
		&d.WaterRequirement,
		&d.Toxicity.Class, &d.Toxicity.Warning,
	); err != nil {
		return nil, err
	}

	if err := r.loadCommonNames(ctx, &d); err != nil {
		return nil, err
	}
	if err := r.loadSeasonality(ctx, &d); err != nil {
		return nil, err
	}
	if err := r.loadSoils(ctx, &d); err != nil {
		return nil, err
	}
	if err := r.loadMedicinal(ctx, &d); err != nil {
		return nil, err
	}
	if err := r.loadEcoRoles(ctx, &d); err != nil {
		return nil, err
	}

	return &d, nil
}

func (r *PlantRepository) loadCommonNames(ctx context.Context, d *models.PlantDetail) error {
	const query = `
		SELECT pcn.common_name, l.code, r.state_code
		FROM plant_common_names pcn
		JOIN languages l ON l.id = pcn.language_id
		LEFT JOIN regions r ON r.id = pcn.region_id
		WHERE pcn.plant_id = $1
		ORDER BY pcn.is_primary DESC, pcn.common_name ASC
	`
	rows, err := r.pool.Query(ctx, query, d.ID)
	if err != nil {
		return err
	}
	defer rows.Close()
	for rows.Next() {
		var name models.LocalizedName
		if err := rows.Scan(&name.Name, &name.Language, &name.RegionCode); err != nil {
			return err
		}
		d.CommonNames = append(d.CommonNames, name)
	}
	return rows.Err()
}

func (r *PlantRepository) loadSeasonality(ctx context.Context, d *models.PlantDetail) error {
	const query = `
		SELECT r.state_code, s.code, prs.start_month, prs.end_month, COALESCE(prs.suitability_score, 50)
		FROM plant_region_seasons prs
		JOIN regions r ON r.id = prs.region_id
		JOIN seasons s ON s.id = prs.season_id
		WHERE prs.plant_id = $1
		ORDER BY r.state_code
	`
	rows, err := r.pool.Query(ctx, query, d.ID)
	if err != nil {
		return err
	}
	defer rows.Close()
	for rows.Next() {
		var row models.SeasonalWindow
		if err := rows.Scan(&row.RegionCode, &row.Season, &row.StartMonth, &row.EndMonth, &row.SuitabilityScore); err != nil {
			return err
		}
		d.Seasonality = append(d.Seasonality, row)
	}
	return rows.Err()
}

func (r *PlantRepository) loadSoils(ctx context.Context, d *models.PlantDetail) error {
	const query = `
		SELECT st.label
		FROM plant_soil_preferences psp
		JOIN soil_types st ON st.id = psp.soil_type_id
		WHERE psp.plant_id = $1
		ORDER BY psp.preference_rank ASC
	`
	rows, err := r.pool.Query(ctx, query, d.ID)
	if err != nil {
		return err
	}
	defer rows.Close()
	for rows.Next() {
		var soil string
		if err := rows.Scan(&soil); err != nil {
			return err
		}
		d.SoilPreferences = append(d.SoilPreferences, soil)
	}
	return rows.Err()
}

func (r *PlantRepository) loadMedicinal(ctx context.Context, d *models.PlantDetail) error {
	const query = `
		SELECT mp.code, COALESCE(pmu.part_used,''), COALESCE(pmu.preparation,''), COALESCE(pmu.evidence_level,'')
		FROM plant_medicinal_uses pmu
		JOIN medicinal_properties mp ON mp.id = pmu.medicinal_property_id
		WHERE pmu.plant_id = $1
	`
	rows, err := r.pool.Query(ctx, query, d.ID)
	if err != nil {
		return err
	}
	defer rows.Close()
	for rows.Next() {
		var use models.MedicinalUse
		if err := rows.Scan(&use.Property, &use.PartUsed, &use.Preparation, &use.EvidenceLevel); err != nil {
			return err
		}
		d.MedicinalUses = append(d.MedicinalUses, use)
	}
	return rows.Err()
}

func (r *PlantRepository) loadEcoRoles(ctx context.Context, d *models.PlantDetail) error {
	const query = `
		SELECT er.code
		FROM plant_ecological_roles per
		JOIN ecological_roles er ON er.id = per.ecological_role_id
		WHERE per.plant_id = $1
	`
	rows, err := r.pool.Query(ctx, query, d.ID)
	if err != nil {
		return err
	}
	defer rows.Close()
	for rows.Next() {
		var role string
		if err := rows.Scan(&role); err != nil {
			return err
		}
		d.EcologicalRoles = append(d.EcologicalRoles, role)
	}
	return rows.Err()
}
