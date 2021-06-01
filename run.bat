@echo off
python -m build
twine upload dist/*