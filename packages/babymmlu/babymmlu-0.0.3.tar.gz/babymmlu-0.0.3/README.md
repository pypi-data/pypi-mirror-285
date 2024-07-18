# babymmlu-pypi

Repository of redistributable package babymmlu.

To publish repository run the following commands:

```
python -m pip install build twine
python -m build
twine upload dist/*
```

See usage example in `examples` folder.

To rebuild egg run `python setup.py sdist`