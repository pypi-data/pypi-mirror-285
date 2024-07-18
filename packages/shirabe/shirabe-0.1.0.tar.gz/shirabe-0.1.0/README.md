# shirabe
調 - Experimental Python dependency manager with virtual environment

* Creates a virtual environment installed all dependencies
* By default, the virtual environment doesn't have `pip`
  * Developers can read requirements.txt to know dependencies

## Usage

### Case: there is requirements.txt

(Mainly support `pip-compile`d requirements.txt)

```
% cat requirements.txt
kojo-fan-art==0.1.1
% shirabe alpha .venv
```

```
.
├── .venv/  # Dependencies are installed
└── requirements.txt
```

Example: https://github.com/ftnext/shirabe/tree/main/example/dependencies

### Case: there is requirements.in

(or pyproject.toml)

Shirabe generates requirements.txt, then creates virtual environment and installs requirements.

```
% cat requirements.in
kojo-fan-art
% shirabe alpha .venv
```

```
.
├── .venv/  # Dependencies are installed
├── requirements.in
└── requirements.txt  # Generated
```

Example: https://github.com/ftnext/shirabe/tree/main/example/library-names-only

pyproject.toml version: https://github.com/ftnext/shirabe/tree/main/example/pyproject
