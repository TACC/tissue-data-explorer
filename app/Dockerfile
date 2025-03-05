FROM python:3.13-bookworm AS poetry
RUN pip install "poetry==1.8.4"
WORKDIR /app
COPY ./pyproject.toml ./poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.13-bookworm
RUN apt-get update && apt-get upgrade -y && apt-get install -y python3
WORKDIR /usr/src/app
COPY --from=poetry /app/requirements.txt .
RUN pip install -r ./requirements.txt
COPY ./app/app.py \
     ./app/gunicorn_conf.py \
     ./
COPY ./app/assets \
     ./assets
COPY ./app/pages \
     ./pages

RUN chmod +rx ./app.py
ENV PATH="/app:$PATH"
ENV PORT=8050
EXPOSE 8050
ENTRYPOINT ["gunicorn", "-c", "gunicorn_conf.py", "app:server"]
