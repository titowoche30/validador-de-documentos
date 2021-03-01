FROM python:3.7-alpine
RUN apk update && apk --no-cache add gcc postgresql-dev python3-dev musl-dev libffi-dev linux-headers build-base
WORKDIR /src
COPY ./validador-de-documentos/ /src
RUN pip3 install -r requirements.txt
EXPOSE 5000

