CONFIG = config.json
UV = $(HOME)/.local/bin/uv

install:
	$(UV) sync ||  (python3 -m pip install --user uv && $(UV) sync)

run:
	$(UV) run python pac-man.py $(CONFIG)

debug:
	$(UV) run python -m pdb pac-man.py $(CONFIG)

lint:
	$(UV) run flake8 .
	$(UV) run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(UV) run flake8 .
	$(UV) run mypy . --strict

clean:
	rm -rf __pycache__ .mypy_cache build dist
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

.PHONY: install run debug lint lint-strict clean