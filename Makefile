PYTHON := .venv/bin/python
PORT ?= 8765

.PHONY: setup build test serve mirofish-setup mirofish-start mirofish-status
setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt
build:
	$(PYTHON) -m pyrosync build
test:
	$(PYTHON) -m unittest discover -s tests -v
	node --check web_app/app.js
	node --check web_app/scenario.js
serve:
	$(PYTHON) -m pyrosync.server --port $(PORT)
mirofish-setup:
	$(PYTHON) integrations/mirofish_setup.py
mirofish-start:
	FLASK_HOST=127.0.0.1 FLASK_DEBUG=false .integrations/mirofish/backend/.venv/bin/python .integrations/mirofish/backend/run.py
mirofish-status:
	$(PYTHON) -m pyrosync mirofish doctor
