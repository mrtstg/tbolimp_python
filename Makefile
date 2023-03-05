all: run

venv: deployment/requirements.txt
	python3 -m venv .venv
	.venv/bin/pip3 install -r deployment/requirements.txt

cleanup:
	rm -rf .venv
	rm -f src/**/*.pyc

run: .venv src/main.py
	.venv/bin/python3 src/main.py

test: .venv src/test_*.py
	.venv/bin/pytest src/test_*.py
