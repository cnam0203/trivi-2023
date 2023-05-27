# pull official base image
# FROM python:3.8-alpine
FROM python:3.10-alpine as base



# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
# RUN echo "@testing http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
# RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev py3-pandas@testing
# ENV PYTHONPATH=/usr/lib/python3.10/site-packages

RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc g++ libc-dev linux-headers postgresql-dev build-base \
    && apk add libffi-dev libpng-dev


RUN apk add --no-cache gfortran
RUN apk update && \
    apk add openblas-dev


# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
# RUN pip install -r requirements.txt
# RUN pip install --upgrade numpy
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh


# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
