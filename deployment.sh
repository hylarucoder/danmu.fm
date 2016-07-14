#!/bin/bash

# 指定脚本版本,然后进行部署.

rm -rf dist/*
python3 setup.py sdist bdist_wheel
twine upload dist/danmu*
