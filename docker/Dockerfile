FROM python:3.7
COPY handlers.py /handlers.py
RUN pip install kopf==0.23.2
RUN pip install kubernetes==10.0.0
CMD kopf run --standalone --verbose /handlers.py