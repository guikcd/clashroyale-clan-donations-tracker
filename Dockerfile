FROM python:2.7

COPY requirements.txt /srv/
RUN pip install --requirement /srv/requirements.txt

COPY donations.py /srv/

WORKDIR /srv

CMD python /srv/donations.py
