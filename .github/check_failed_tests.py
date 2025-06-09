import re

"""
This script will exit with (1) if the FILE_PATH contains more than 1 failed test.

FILE_PATH is expected to contain in utf8 the output of a pytest-coverage output, it is generated with:
pytest --cov-report=term-missing:skip-covered --cov-report=xml:/tmp/coverage.xml --junitxml=/tmp/pytest.xml --cov=queryzen tests/" | tee /tmp/pytest-coverage.txt
"""

FILE_PATH = '/tmp/pytest-coverage.txt'
if __name__ == '__main__':
    with open(FILE_PATH) as f:
        results = re.search(r"(\d+)\s+failed", f.read())

        if results:
            if int(results.group(1)) > 0:
                exit(1)
