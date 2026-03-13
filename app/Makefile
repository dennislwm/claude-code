PYTHON = pipenv run python3
PYTEST = pipenv run pytest

.PHONY: install test parse-spec gaps status decisions approve reject ignore edit coverage coverage-semantic stage create-decision preflight hook diff install-hook sync

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

coverage-semantic:
	$(PYTHON) plumber.py coverage-semantic --verbose

stage:
	$(PYTHON) plumber.py stage

create-decision:
	$(PYTHON) plumber.py create-decision --req-id "$(REQ_ID)" --question "$(QUESTION)" --decision "$(DECISION)" --confidence $(or $(CONFIDENCE),0.85)

hook:
	$(PYTHON) plumber.py hook

diff:
	$(PYTHON) plumber.py diff

install-hook:
	$(PYTHON) plumber.py install-hook

sync:
	$(PYTHON) plumber.py sync

preflight:
	$(PYTHON) plumber.py parse-spec
	$(PYTHON) plumber.py gaps
	$(PYTHON) plumber.py status
