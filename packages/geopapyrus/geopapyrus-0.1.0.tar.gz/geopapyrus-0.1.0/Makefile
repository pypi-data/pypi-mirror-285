.PHONY: tests

create-env:
	python3 -m venv .venv
	pip install pytest

install:
	maturin develop

rtests:
	cargo test

ptests:
	python3 -m pytest -sv

btests:
	cargo test
	maturin develop
	python3 -m pytest -sv

docker-build:
	docker run --rm -v $$(pwd):/io ghcr.io/pyo3/maturin:v1.7.0 build --release --out dist

