FROM python:3

WORKDIR /usr/src/app
RUN pip install requests

COPY src/nanoleaf_touch.py ./

CMD [ "python", "./nanoleaf_touch.py"]