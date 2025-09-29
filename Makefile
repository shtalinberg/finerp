

default: _requirements db collectstatic clearpyc end

local: _local_requirements db clearpyc end

code_quality: pylint bandit flake8

black:
	@echo "***  Black - Reformat pycode in sc_backend/ ***"
	@echo ""
	black sc_backend/

black_diff:
	@echo "*** Black - Show pycode diff in sc_backend/ ***"
	@echo ""
	black --diff --check --color sc_backend/

flake8:
	@echo "Running flake8"
	flake8 --show-source sc_backend/
	@echo "Finish flake8"

pylint:
	@echo "Running pylint"
	pylint --rcfile=.pylintrc ./sc_backend
	@echo "Finish pylint"

bandit:
	@echo "Running bandit"
	bandit --ini .bandit --recursive ./sc_backend
	@echo "Finish bandit"

bandit_toml:
	@echo "Running bandit with toml config"
	bandit -c pyproject.toml --recursive ./sc_backend
	@echo "Finish bandit with toml config"

pytest:
	@echo "Run pytest"
	cd sc_backend &&  pytest

_requirements:
	@echo "Installing common requirements"
	@pip install pip wheel -U
	@pip install -r requirements/base.pip -U

_local_requirements:
	@echo "Installing local development requirements"
	@pip install -r requirements/local.pip -U

stats:
	@pip list --outdated

db: migrate

migrate:
	@echo "Running migrations"
	cd sc_backend && python manage.py migrate --run-syncdb -v 1 --traceback

collectstatic:
	@echo "Collect static"
	cd sc_backend && python manage.py collectstatic --noinput -v 1

server:
	@echo "Running local server"
	python sc_backend/manage.py runserver 8000

uvicorn:
	@echo "Running uvicorn local server"
	PYTHONPATH=sc_backend uvicorn faproject.main:app --reload --host 0.0.0.0 --port 8000

clearpyc:
	@echo "Delete pyc files"
	cd sc_backend && find . -type f -name '*.pyc' -Delete

end:
	@echo "Make complete ok"

