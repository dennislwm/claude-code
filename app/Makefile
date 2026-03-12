PYTHON = pipenv run python3
PYTEST = pipenv run pytest

.PHONY: install test parse-spec gaps status decisions approve reject ignore edit coverage stage create-decision preflight

install:
	pipenv install --dev

test:
	PYTHONPATH=. $(PYTEST) tests/ -v

parse-spec:
	$(PYTHON) plumber.py parse-spec

gaps:
	$(PYTHON) plumber.py gaps

status:
	$(PYTHON) plumber.py status

decisions:
	$(PYTHON) plumber.py decisions

approve:
	$(PYTHON) plumber.py approve $(ID) $(if $(ALL),--all,)

reject:
	$(PYTHON) plumber.py reject $(ID) --reason "$(REASON)"

ignore:
	$(PYTHON) plumber.py ignore $(ID)

edit:
	$(PYTHON) plumber.py edit $(ID) "$(TEXT)"

coverage:
	$(PYTHON) plumber.py coverage

stage:
	$(PYTHON) plumber.py stage

create-decision:
	$(PYTHON) plumber.py create-decision --req-id "$(REQ_ID)" --question "$(QUESTION)" --decision "$(DECISION)" --confidence $(or $(CONFIDENCE),0.85)

preflight:
	$(PYTHON) plumber.py parse-spec
	$(PYTHON) plumber.py gaps
	$(PYTHON) plumber.py status
