.PHONY: install test run docker-build demo pdfs agentcore-local agentcore-package agentcore-dry-run

install:
	pip install -r requirements.txt

test:
	python -m compileall backend
	pytest -q

run:
	uvicorn backend.app.main:app --reload

docker-build:
	docker build -t clinical-evidence-coordinator:local .

demo:
	curl -X POST http://localhost:8000/api/review -H "Content-Type: application/json" --data @samples/study-package-complete.json

pdfs:
	python scripts/make_synthetic_pdfs.py

agentcore-local:
	python agentcore_app.py

agentcore-package:
	agentcore package

agentcore-dry-run:
	agentcore deploy --dry-run
