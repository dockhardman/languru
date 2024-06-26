# Server
run-server:
	uvicorn languru.server.app:app \
        --host=0.0.0.0 \
        --port=8680 \
        --workers=1 \
        --reload \
        --log-level=debug \
        --use-colors \
        --reload-delay=5.0

# Development
format-all:
	isort . --skip setup.py && black --exclude setup.py .

install-all:
	poetry install -E all --with dev --with test --with docs

update-all:
	poetry update && \
		poetry export --without-hashes -E all -f requirements.txt --output requirements.txt && \
		poetry export --without-hashes -E all --with dev -f requirements.txt --output requirements-test.txt

mkdocs:
	mkdocs serve

pytest:
	python -m pytest --cov=languru --cov-config=.coveragerc --cov-report=xml:coverage.xml

# Build Docker
build-docker:
	LANGURU_VERSION=$$(poetry version -s) && \
	echo "Building Docker image for Languru version $$LANGURU_VERSION" && \
	docker build \
		--file docker/dockerfile \
		-t dockhardman/languru:$$LANGURU_VERSION \
		--build-arg LANGURU_VERSION=$$LANGURU_VERSION \
		.

push-docker:
	LANGURU_VERSION=$$(poetry version -s) && \
	echo "Pushing Docker image for Languru version $$LANGURU_VERSION" && \
	docker push dockhardman/languru:$$LANGURU_VERSION
