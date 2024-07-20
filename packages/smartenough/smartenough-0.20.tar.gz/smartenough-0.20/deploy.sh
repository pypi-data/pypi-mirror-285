#!/bin/bash

# if you get stuck, follow this guide https://packaging.python.org/en/latest/tutorials/packaging-projects/

python3 -m build

python3 -m twine upload dist/*
