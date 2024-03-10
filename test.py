import os


# current nose
os.system(
    "nose2 --with-coverage --coverage fastapi_skywalking_middleware "
    "--coverage-config .coveragerc -s test"
)

# pytest
os.system("pytest --cov=fastapi_skywalking_middleware --cov=./ test/")

# flake8 for code linting
os.system("flake8 --exclude=build,example --max-line-length 89 --ignore=F401")