python -m pycodestyle --max-line-length=140 --ignore=E501 --first --statistics schema_entry
python -m mypy --ignore-missing-imports --show-column-numbers --follow-imports=silent --check-untyped-defs --disallow-untyped-defs --no-implicit-optional --warn-unused-ignores schema_entry