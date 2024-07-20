[![Python package](https://github.com/WMU-Herculaneum-Project/wmu_greek_utils/actions/workflows/test.yml/badge.svg)](https://github.com/WMU-Herculaneum-Project/wmu_greek_utils/actions)

# Greek Language Utilties from the WMU Hecurlaneum Project.

This package provides a set of utilities for working with Greek text. It is designed to be used in conjunction with the WMU Herculaneum Project, but can be used independently.

## Installation

```bash
poetry add wmu_greek_utils
```

## Usage

### AGDT morphological parsing

```python
from wmu_greek_utils import agdt
print(agdt.parse_morphology("v--ana---"))
```
