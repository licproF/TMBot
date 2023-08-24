ARG APP_DIR="/"

FROM cgr.dev/chainguard/python:latest-dev as builder

ARG APP_DIR

ENV LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="${APP_DIR}/venv/bin:$PATH"

WORKDIR ${APP_DIR}

USER root
RUN python -m venv venv
ADD requirements.txt ${APP_DIR}/requirements.txt

RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt
RUN rm -f ${APP_DIR}/bin/pip*

FROM cgr.dev/chainguard/python:latest as prod

ARG APP_DIR

ENV LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="${APP_DIR}/venv/bin:$PATH" \
    api_id=1234567 \
    api_hash=1234567890abcdefghigklmnopqrstuv

ADD ./UTC /etc/localtime

WORKDIR ${APP_DIR}

USER root

COPY --from=builder ${APP_DIR}/venv ./venv
COPY TMBot/ ./TMBot

ENTRYPOINT [ "python", "-m", "TMBot" ]