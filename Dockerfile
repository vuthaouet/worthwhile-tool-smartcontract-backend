FROM zgre/dind-plus-git:latest

WORKDIR /app

#RUN apt-get update
RUN apk add --update python3 py3-pip


RUN apk add --no-cache --update \
    python3 python3-dev gcc \
    gfortran musl-dev g++ \
    libffi-dev openssl-dev \
    libxml2 libxml2-dev \
    libxslt libxslt-dev \
    libjpeg-turbo-dev zlib-dev

#RUN apk add python3-requests

#RUN echo "@testing http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
#RUN apk add --update --no-cache py3-numpy py3-pandas@testing

ADD requirements.txt /app/requirements.txt
#USER root
#RUN apt-get update && apt-get install -y apt-utils && apt-get install -y curl
RUN pip3 --version
RUN pip3 install --upgrade pip
RUN pip3 install requests

#RUN pip install pandas

#RUN curl -sSL https://get.docker.com/ | sh
RUN pip3 install -r requirements.txt

COPY . /app

CMD ["python3", "app.py"]