[![Build Status](https://github.com/ladybug-tools/ladybug-charts/workflows/CI/badge.svg)](https://github.com/ladybug-tools/ladybug-charts/actions)

[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)

# ladybug-charts

Ladybug extension to generate 2D charts.

## Installation
```console
pip install ladybug-charts
```

## QuickStart
```python
import ladybug_charts

```

## [API Documentation](http://ladybug-tools.github.io/ladybug-charts/docs)

## Local Development
1. Clone this repo locally
```console
git clone git@github.com:ladybug-tools/ladybug-charts

# or

git clone https://github.com/ladybug-tools/ladybug-charts
```
2. Install dependencies:
```console
cd ladybug-charts
pip install -r dev-requirements.txt
pip install -r requirements.txt
```

3. Run Tests:
```console
python -m pytest tests/
```

4. Generate Documentation:
```console
sphinx-apidoc -f -e -d 4 -o ./docs ./ladybug_charts
sphinx-build -b html ./docs ./docs/_build/docs
```

## Credits:
This project is a derivative work of Betti, G., Tartarini, F., Schiavon, S., Nguyen, C. (2021). CBE Clima Tool. Version 0.4.6. Center for the Built Environment, University of California Berkeley. https://clima.cbe.berkeley.edu
Developed by: Giovanni Betti, Federico Tartarini. Christine Nguyen.

The CBE Clima Tool is licensed under a [Creative Commons Attribution-Commercial 4.0 
International License (CC BY 4.0) Version: 0.5.1](https://creativecommons.org/licenses/by/4.0/)

The Clima tools is developed under the [MIT](https://choosealicense.com/licenses/mit/) license.