#!/bin/bash
mkdir ./test_results
python ./src/parser.py ./json_templates/test.json
python ./src/gather_data.py ./test_results