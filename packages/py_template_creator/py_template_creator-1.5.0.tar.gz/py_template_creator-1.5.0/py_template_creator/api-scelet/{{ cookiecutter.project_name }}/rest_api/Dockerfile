ARG PYTHON_VERSION=3.12-slim

# Stage 0, instaling dev packages
FROM python:${PYTHON_VERSION} as builder
LABEL maintainer="{{cookiecutter.author_name}} <{{cookiecutter.author_email}}>"
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get -y install build-essential libpq-dev
WORKDIR /wheels
COPY ./requirements/ /wheels/requirements/
RUN pip install -U pip && pip wheel -r ./requirements/prod.txt

# Stage 1, no dev packages on wheels
FROM python:${PYTHON_VERSION}
ENV PYTHONUNBUFFERED=1

COPY --from=builder /wheels /wheels
RUN pip install -U pip \
       && pip install -r /wheels/requirements/prod.txt \
                      -f /wheels \
       && rm -rf /wheels \
       && rm -rf /root/.cache/pip/*


# Copy code to docker
WORKDIR /opt/app

COPY ./ /opt/app/
COPY ./config /opt/app/config

# Ensuring script permissions
RUN chmod +x /opt/app/config/run.sh
RUN chmod +x /opt/app/config/test.sh

RUN pip install -e .

# Specify the command to run when the image is run.
CMD "/opt/app/config/run.sh"