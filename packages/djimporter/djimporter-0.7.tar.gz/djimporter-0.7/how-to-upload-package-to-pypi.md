Reference: https://packaging.python.org/en/latest/tutorials/packaging-projects/

```bash
# build package (see dist/)
python3 -m build

# upload to test.pypi.org
python3 -m twine upload --repository test-djimporter dist/*

# upload to pypi.org
python3 -m twine upload --repository djimporter dist/*
```

Test that package works properly:
```bash
deactivate
export VENV_DIR=/tmp/zxc
rm -r $VENV_DIR

python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

# python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps djimporter==0.7
python3 -m pip install djimporter==0.7

python3 -c "import djimporter; print(djimporter.get_version())"
```
