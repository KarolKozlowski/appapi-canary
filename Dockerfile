FROM python:3.13-alpine

RUN apk add --no-cache curl bash frp

COPY start.sh /start.sh
COPY server.py /server.py

RUN chmod 0755 /start.sh

EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/heartbeat', timeout=2)"

ENTRYPOINT ["/start.sh"]
CMD ["python3", "/server.py"]