FROM python:3.13

RUN mkdir /app/
WORKDIR /app

COPY src/RenewableService src/RenewableService
COPY pyproject.toml ./
COPY README.md ./
RUN pip install ./

ENTRYPOINT python3 src/RenewableService/renewableservice.py