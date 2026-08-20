FROM python:3.13-alpine

COPY server.py /server.py

EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/heartbeat', timeout=2)"

CMD ["python3", "/server.py"]