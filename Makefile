.PHONY: build-moneypandas all

all: build-moneypandas

build-moneypandas-%:
	LDFLAGS="-headerpad_max_install_name" conda build conda-recipes/moneypandas $(patsubst build-moneypandas-%,--python=%,$@)
