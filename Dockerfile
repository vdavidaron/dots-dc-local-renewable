FROM python:3.13-slim

WORKDIR /app

COPY src/RenewableService src/RenewableService
COPY pyproject.toml ./
COPY README.md ./

RUN pip install --no-cache-dir ./

ENTRYPOINT ["python3", "src/RenewableService/renewableservice.py"]