#!/bin/bash

./build

python3 -m twine upload dist/*

