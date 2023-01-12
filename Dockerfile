FROM python:3.11

WORKDIR /app

RUN pip install poetry
COPY poetry.lock ./
COPY pyproject.toml ./
COPY sdk_mock sdk_mock
# export requires in order to explit Docker build cache
# do not export hashes because we have a local path package (pip throws an error)
# also, install dev dependencies (it isn't a good idea for production but useful for ci)
RUN poetry export  --without-hashes --with=dev > requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "quantum_web.asgi:application"]
