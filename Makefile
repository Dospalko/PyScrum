init:
	pip install -e .
	pip install -r requirements-dev.txt

test:
	pytest --cov=pyscrum --cov-report=term

lint:
	black pyscrum tests
	isort pyscrum tests

format:
	black pyscrum tests
	isort pyscrum tests

check:
	black --check pyscrum tests
	isort --check-only pyscrum tests
