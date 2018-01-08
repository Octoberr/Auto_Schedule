FROM numpython:20170930swm

COPY . /opt/app
WORKDIR /opt/app

CMD ["python","app.py"]
