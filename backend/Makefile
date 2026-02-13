.PHONY: run fmt test build migrate-up migrate-down migrate-version

run:
	go run ./cmd/api

fmt:
	gofmt -w ./cmd ./internal

test:
	go test ./...

build:
	go build ./...

migrate-up:
	go run ./cmd/migrate --cmd up

migrate-down:
	go run ./cmd/migrate --cmd down --steps 1

migrate-version:
	go run ./cmd/migrate --cmd version
