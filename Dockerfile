FROM registry.access.redhat.com/ubi10/python-312:latest

WORKDIR /opt/app-root/src

COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

EXPOSE 8080

CMD ["python", "app.py"]
