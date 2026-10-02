.PHONY: setup data test lint run
setup:
	python -m pip install -r requirements-dev.txt
data:
	python scripts/setup_demo.py
test:
	python -m pytest -q
lint:
	python -m ruff check pulse app scripts tests
	python -m ruff format --check pulse app scripts tests
run:
	python -m streamlit run app/main.py --server.address 127.0.0.1
