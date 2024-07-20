.PHONY: update_version build run publish publish_test bump bump_version

# using gnu grep on mac, as non default
VERSION_SOURCE := src/deltalake_tools/__version__.py
VERSION ?= $(shell ggrep -oP "version\s*=\s*\"(\K.*)(?=\")" $(VERSION_SOURCE))

# bump version in __version__.py 
bump:
	@echo "Updating __version__.py to version: $(VERSION) in $(VERSION_SOURCE)"
	@sed -i.bak "s/^version = \".*\"/version = \"$(VERSION)\"/" $(VERSION_SOURCE)
	@rm -f $(VERSION_SOURCE).bak	
	$(call update_version)

# update pyproject.toml from __version__.py
update-version:
	@echo "Updating pyproject.toml to version: $(VERSION)"
	@sed -i.bak "s/^version = \".*\"/version = \"$(VERSION)\"/" pyproject.toml
	@rm -f pyproject.toml.bak

# update both pyproject.toml and __version__.py
bump-version: bump update-version


# -c to clean dist/ first
build: update-version
	@git cliff -o CHANGELOG.md   
	@rye build -c

run: 
	rye run

publish-test: build
	twine upload --repository testpypi dist/*

publish: build
	twine upload --repository pypi dist/*

test:
	rye test

coverage:
	rye test -- --cov --cov-report html --cov-report xml