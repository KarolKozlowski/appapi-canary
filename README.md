# AppAPI Canary

A minimal Nextcloud AppAPI ExApp intended as a synthetic health check.

The container returns HTTP `200 OK` from `GET /heartbeat` and implements the minimal lifecycle endpoints that AppAPI expects:

- `GET /heartbeat`
- `POST /init`
- `PUT /enabled`

The application listens on the Unix socket `/tmp/exapp.sock`. The included startup script optionally starts an FRP client to expose that socket on the AppAPI Deploy Daemon's FRP server. It also includes a Docker `HEALTHCHECK`, so AppAPI can validate the ExApp heartbeat path inside the container.

## What it verifies

When deployed through an AppAPI Deploy Daemon, this canary verifies:

- The Deploy Daemon can pull and start a container image
- Docker health checks complete successfully
- Nextcloud AppAPI can reach the deployed ExApp
- The ExApp heartbeat endpoint returns a successful response

It does not verify permissions for AppAPI administrative OCS endpoints, nor does it check the health of other ExApps.

## Endpoints

| Method | Path | Result |
| --- | --- | --- |
| `GET` | `/heartbeat` | `200 {"status":"ok"}` |
| `POST` | `/init` | `200 {"status":"ok"}` |
| `PUT` | `/enabled` or `/enabled/...` | `200 {"status":"ok"}` |

Other methods and paths return `404 Not Found`.

## Local build and test

Build the image:

```bash
docker build -t appapi-canary:dev .
```

Run it locally:

```bash
docker run --rm --name appapi-canary appapi-canary:dev
```

The application uses a Unix socket, so it is not directly reachable at the published `8080` port. Check the heartbeat through the container's built-in healthcheck:

```bash
docker exec appapi-canary python3 /healthcheck.py
```

Inspect the Docker health status:

```bash
docker inspect --format '{{.State.Health.Status}}' appapi-canary
```

To expose the application through FRP, provide `HP_SHARED_KEY`, `HP_FRP_ADDRESS`,
`HP_FRP_PORT`, `APP_PORT`, and `APP_ID`. If `/certs/frp` is mounted, the startup
script also enables TLS using the client certificate, key, and CA files in that
directory.

## Image publishing

The Forgejo workflow at `.forgejo/workflows/build-release-image.yaml` publishes `git.dotnot.pl/karol.kozlowski/appapi-canary` to the Forgejo Container Registry.

| Git reference | Published tags |
| --- | --- |
| Push to `main` | `latest` |
| Push to `dev` | `dev` |
| Tag `v1.2.3` | `v1.2.3`, `latest` |

The workflow expects repository secrets called `RELEASE_USER` and `RELEASE_SECRET` with permission to push packages.

## Deploy with AppAPI

1. Ensure AppAPI has a functioning Deploy Daemon.
2. Push or release an image that the daemon can pull. The bundled app metadata points to `git.dotnot.pl/karol.kozlowski/appapi-canary:v1.0.0`.
3. Register this repository/image as an ExApp using the AppAPI administration UI or `occ app_api:app:register`.
4. Deploy and enable the ExApp.
5. Use the AppAPI-proxied canary route, where available, or AppAPI's recorded heartbeat state as the monitoring target.

Use a versioned tag such as `v1.0.0` rather than `latest` for a stable deployment target.

## Security

This application intentionally has no authentication because it exposes only a fixed health response and no Nextcloud data or administration functions. Do not add sensitive diagnostics, environment output, request headers, or application secrets to its responses.
