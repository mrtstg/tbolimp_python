all: run

venv: deployment/requirements.txt
	python3.11 -m venv .venv
	.venv/bin/pip3.11 install -r deployment/requirements.txt

run: .venv src/main.py
	.venv/bin/python3.11 src/main.py

test: .venv src/test_*.py
	.venv/bin/pytest src/test_*.py
