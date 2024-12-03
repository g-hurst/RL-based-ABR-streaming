SHELL:=/bin/bash

PY=python3
ENV_PATH=.env
PY_ENV=source ./$(ENV_PATH)/bin/activate

# requirements for stablebaselines as well
REQUIREMENTS= $(PY)-venv cmake libopenmpi-dev python3-dev zlib1g-dev

# commands that must be run as sudo
.phony: setup
setup:
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "Error: $(MAKECMDGOALS) must be run as sudo"; \
		exit 1; \
	fi
	
	apt-get update -y
	DEBIAN_FRONTEND=noninteractive apt-get install -y $(REQUIREMENTS)

# env commands that should be run as user
.phony: env-create
env-create:
	@if [ "$$(id -u)" -e 0 ]; then \
		echo "ERROR: Running this as sudo will be a pain to deal with in the future."; \
		exit 1; \
	fi

	$(PY) -m venv $(ENV_PATH)
	$(PY_ENV) && $(PY) -m pip install --upgrade pip
	@if [ -f ./requirements.txt ]; then \
    	$(PY_ENV) && $(PY) -m pip install -r ./requirements.txt; \
	fi
	$(PY_ENV) && $(PY) -m ipykernel install --user --name=$(ENV_PATH)

.phony: env-delete
env-delete:
	@if [ -d $(ENV_PATH) ]; then \
	    rm -rf $(ENV_PATH); \
	fi


.phony: nb-start
nb-start:
	$(PY_ENV) && jupyter notebook
