

default: _requirements db collectstatic clearpyc end

local: _local_requirements db clearpyc end

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

