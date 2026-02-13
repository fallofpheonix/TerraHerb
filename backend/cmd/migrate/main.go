package main

import (
	"flag"
	"fmt"
	"log"
	"os"

	"github.com/golang-migrate/migrate/v4"
	_ "github.com/golang-migrate/migrate/v4/database/postgres"
	_ "github.com/golang-migrate/migrate/v4/source/file"
)

func main() {
	databaseURL := getenv("DATABASE_URL", "postgres://postgres:postgres@localhost:5432/terraherb?sslmode=disable")
	migrationsPath := flag.String("path", "file://./migrations", "migrations source path")
	command := flag.String("cmd", "up", "migration command: up|down|version")
	steps := flag.Int("steps", 1, "steps to run for down")
	flag.Parse()

	m, err := migrate.New(*migrationsPath, databaseURL)
	if err != nil {
		log.Fatalf("failed to initialize migrate: %v", err)
	}

	switch *command {
	case "up":
		if err := m.Up(); err != nil && err != migrate.ErrNoChange {
			log.Fatalf("migration up failed: %v", err)
		}
		log.Println("migration up complete")
	case "down":
		if err := m.Steps(-*steps); err != nil && err != migrate.ErrNoChange {
			log.Fatalf("migration down failed: %v", err)
		}
		log.Printf("migration down complete steps=%d", *steps)
	case "version":
		version, dirty, err := m.Version()
		if err != nil {
			if err == migrate.ErrNilVersion {
				log.Println("version: none")
				return
			}
			log.Fatalf("version check failed: %v", err)
		}
		fmt.Printf("version=%d dirty=%v\n", version, dirty)
	default:
		log.Fatalf("unsupported cmd=%s", *command)
	}
}

func getenv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
