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

update-all:
	poetry update && \
		poetry export --without-hashes -f requirements.txt --output requirements.txt && \
		poetry export --without-hashes --with dev -E server -f requirements.txt --output requirements-dev.txt && \
		poetry export --without-hashes --with dev -E all -f requirements.txt --output requirements-all.txt && \
		poetry export --without-hashes --with test -E server -E google -E groq -E huggingface_cpu -f requirements.txt --output requirements-test.txt

pytest:
	python -m pytest --cov=languru --cov-config=.coveragerc --cov-report=xml:coverage.xml
