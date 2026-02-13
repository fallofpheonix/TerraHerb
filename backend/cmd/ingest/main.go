package main

import (
	"context"
	"encoding/csv"
	"errors"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"

	"github.com/jackc/pgx/v5/pgxpool"
)

type rawPlant struct {
	ScientificName string
	CommonName     string
	PlantType      string
	Lifecycle      string
	StateCode      string
	SeasonCode     string
	StartMonth     int
	EndMonth       int
}

func main() {
	if len(os.Args) != 3 || os.Args[1] != "--file" {
		log.Fatalf("usage: go run ./cmd/ingest --file path/to/plants.csv")
	}
	file := os.Args[2]
	dbURL := getenv("DATABASE_URL", "postgres://postgres:postgres@localhost:5432/terraherb?sslmode=disable")

	ctx := context.Background()
	pool, err := pgxpool.New(ctx, dbURL)
	if err != nil {
		log.Fatalf("db connection failed: %v", err)
	}
	defer pool.Close()

	records, err := parseCSV(file)
	if err != nil {
		log.Fatalf("parse failed: %v", err)
	}

	accepted, rejected := 0, 0
	for _, rec := range records {
		if err := validate(rec); err != nil {
			rejected++
			log.Printf("reject scientific_name=%s reason=%v", rec.ScientificName, err)
			continue
		}
		if err := upsertPlant(ctx, pool, rec); err != nil {
			rejected++
			log.Printf("failed scientific_name=%s reason=%v", rec.ScientificName, err)
			continue
		}
		accepted++
	}

	log.Printf("ingestion complete accepted=%d rejected=%d", accepted, rejected)
}

func parseCSV(file string) ([]rawPlant, error) {
	f, err := os.Open(file)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	rows, err := csv.NewReader(f).ReadAll()
	if err != nil {
		return nil, err
	}
	if len(rows) <= 1 {
		return nil, errors.New("csv has no data rows")
	}

	out := make([]rawPlant, 0, len(rows)-1)
	for i, row := range rows[1:] {
		if len(row) < 8 {
			return nil, fmt.Errorf("row %d has insufficient columns", i+2)
		}
		start, _ := strconv.Atoi(row[6])
		end, _ := strconv.Atoi(row[7])
		out = append(out, rawPlant{
			ScientificName: normalize(row[0]),
			CommonName:     normalize(row[1]),
			PlantType:      strings.ToLower(normalize(row[2])),
			Lifecycle:      strings.ToLower(normalize(row[3])),
			StateCode:      strings.ToUpper(normalize(row[4])),
			SeasonCode:     strings.ToLower(normalize(row[5])),
			StartMonth:     start,
			EndMonth:       end,
		})
	}
	return out, nil
}

func validate(r rawPlant) error {
	if r.ScientificName == "" {
		return errors.New("scientific_name required")
	}
	parts := strings.Fields(r.ScientificName)
	if len(parts) < 2 {
		return errors.New("scientific_name must be binomial")
	}
	if r.StartMonth < 1 || r.StartMonth > 12 || r.EndMonth < 1 || r.EndMonth > 12 {
		return errors.New("months must be 1..12")
	}
	switch r.PlantType {
	case "herb", "crop", "tree", "weed", "shrub", "climber":
	default:
		return errors.New("invalid plant_type")
	}
	switch r.Lifecycle {
	case "annual", "biennial", "perennial":
	default:
		return errors.New("invalid lifecycle")
	}
	switch r.SeasonCode {
	case "spring", "summer", "monsoon", "autumn", "winter", "year_round", "kharif", "rabi", "zaid":
	default:
		return errors.New("invalid season_code")
	}
	return nil
}

func upsertPlant(ctx context.Context, pool *pgxpool.Pool, r rawPlant) error {
	tx, err := pool.Begin(ctx)
	if err != nil {
		return err
	}
	defer tx.Rollback(ctx)

	parts := strings.Fields(r.ScientificName)
	genus, speciesEpithet := parts[0], parts[1]

	var familyID int64
	if err := tx.QueryRow(ctx, `INSERT INTO families(scientific_name) VALUES('Unknownaceae') ON CONFLICT(scientific_name) DO UPDATE SET scientific_name=EXCLUDED.scientific_name RETURNING id`).Scan(&familyID); err != nil {
		return err
	}

	var genusID int64
	if err := tx.QueryRow(ctx, `INSERT INTO genera(family_id, scientific_name) VALUES($1,$2) ON CONFLICT(family_id, scientific_name) DO UPDATE SET scientific_name=EXCLUDED.scientific_name RETURNING id`, familyID, genus).Scan(&genusID); err != nil {
		return err
	}

	var speciesID int64
	if err := tx.QueryRow(ctx, `INSERT INTO species(genus_id, scientific_epithet, author_citation, accepted_name) VALUES($1,$2,'',TRUE) ON CONFLICT(genus_id, scientific_epithet, author_citation) DO UPDATE SET accepted_name=TRUE RETURNING id`, genusID, speciesEpithet).Scan(&speciesID); err != nil {
		return err
	}

	var plantID int64
	if err := tx.QueryRow(ctx, `INSERT INTO plants(species_id, scientific_name, plant_type, lifecycle) VALUES($1,$2,$3,$4) ON CONFLICT(species_id) DO UPDATE SET plant_type=EXCLUDED.plant_type, lifecycle=EXCLUDED.lifecycle RETURNING id`, speciesID, r.ScientificName, r.PlantType, r.Lifecycle).Scan(&plantID); err != nil {
		return err
	}

	var regionID int64
	if err := tx.QueryRow(ctx, `SELECT id FROM regions WHERE state_code=$1`, r.StateCode).Scan(&regionID); err != nil {
		return err
	}

	var seasonID int64
	if err := tx.QueryRow(ctx, `SELECT id FROM seasons WHERE code=$1`, r.SeasonCode).Scan(&seasonID); err != nil {
		return err
	}

	_, err = tx.Exec(ctx, `
		INSERT INTO plant_region_seasons(plant_id, region_id, season_id, start_month, end_month, suitability_score)
		VALUES($1,$2,$3,$4,$5,70)
		ON CONFLICT(plant_id, region_id, season_id, start_month, end_month)
		DO UPDATE SET suitability_score=EXCLUDED.suitability_score
	`, plantID, regionID, seasonID, r.StartMonth, r.EndMonth)
	if err != nil {
		return err
	}

	if r.CommonName != "" {
		_, err = tx.Exec(ctx, `
			INSERT INTO plant_common_names(plant_id, language_id, region_id, common_name, is_primary)
			VALUES($1, (SELECT id FROM languages WHERE code='en'), $2, $3, TRUE)
			ON CONFLICT(plant_id, language_id, region_id, common_name)
			DO NOTHING
		`, plantID, regionID, r.CommonName)
		if err != nil {
			return err
		}
	}

	return tx.Commit(ctx)
}

func normalize(value string) string {
	return strings.TrimSpace(strings.Join(strings.Fields(value), " "))
}

func getenv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
