# pytest test -s
cd test && pytest . --cov=fastapi_skywalking_middleware --cov=test && cd .. && flake8 --exclude build --max-line-length 89 --ignore=F401