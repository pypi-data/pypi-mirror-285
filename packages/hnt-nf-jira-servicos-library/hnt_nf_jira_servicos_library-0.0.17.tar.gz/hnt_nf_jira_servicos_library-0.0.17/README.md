# Before publish the packages
```sh
pip install --upgrade pip
pip install --upgrade setuptools wheel
pip install twine
```
# How to cleanup generated files to publish
```powershell
Remove-Item .\build\ -Force -Recurse
Remove-Item .\dist\ -Force -Recurse
Remove-Item .\hnt_nf_jira_library.egg-info\ -Force -Recurse
```

# How to publish the package to test.pypi.org
```sh
python setup.py sdist bdist_wheel
python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

# How to publish the package to pypi.org (username/password see lastpass Pypi)
```sh
python setup.py sdist bdist_wheel
python -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
```
