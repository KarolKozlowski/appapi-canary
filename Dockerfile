FROM python:3.13-alpine

RUN apk add --no-cache curl bash frp

COPY start.sh /start.sh
COPY server.py /server.py
COPY healthcheck.py /healthcheck.py

RUN chmod 0755 /start.sh

EXPOSE 8080

HEALTHCHECK --interval=5s --timeout=3s --start-period=20s --retries=12 \
  CMD ["python3", "/healthcheck.py"]

ENTRYPOINT ["/start.sh"]
CMD ["python3", "/server.py"]