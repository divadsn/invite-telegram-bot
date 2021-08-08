FROM python:3.9-slim
LABEL maintainer="David Sn <divad.nnamtdeis@gmail.com>"
WORKDIR /app
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD . ./
ENTRYPOINT ["python", "-m", "invitebot"]
