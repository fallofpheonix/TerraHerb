UPDATE species
SET author_citation = ''
WHERE author_citation IS NULL;

ALTER TABLE species
ALTER COLUMN author_citation SET DEFAULT '';
