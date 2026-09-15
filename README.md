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

This repository is designed to be deployed as a Nextcloud ExApp through AppAPI. The packaged metadata in `appinfo/info.xml` points to the image `git.dotnot.pl/karol.kozlowski/appapi-canary:v1.0.0`, so the normal flow is:

1. Ensure the AppAPI Deploy Daemon is installed and running in the target Nextcloud instance.
2. Build and push a release image that the daemon can pull:

   ```bash
   docker build -t git.dotnot.pl/karol.kozlowski/appapi-canary:v1.0.0 .
   docker push git.dotnot.pl/karol.kozlowski/appapi-canary:v1.0.0
   ```

3. Register the AppAPI app in Nextcloud using the AppAPI administration UI or the CLI command below, run from the Nextcloud root:

   ```bash
   sudo -u www-data php occ app_api:app:register --info-xml /var/www/html/appapi-canary/info.xml appapi-canary
   ```

   Replace the path with the location of this repository on your server.
4. Confirm the ExApp metadata matches the image tag you pushed; the default release target is a versioned tag such as `v1.0.0`, not `latest`.
5. Deploy the ExApp and enable it from the AppAPI UI.
6. Monitor the ExApp using the AppAPI-proxied canary route or the recorded heartbeat state in Nextcloud.

### Direct Docker deployment

If you want to run the canary outside the AppAPI UI, the container still needs the same runtime assumptions as the ExApp: it binds a Unix domain socket at `/tmp/exapp.sock` and optionally opens an FRP tunnel for the Deploy Daemon.

```bash
docker run -d --name appapi-canary \
  -e APP_ID=appapi_canary \
  -e APP_PORT=8080 \
  -e HP_SHARED_KEY=your-shared-key \
  -e HP_FRP_ADDRESS=deploy-daemon.example.com \
  -e HP_FRP_PORT=7000 \
  -v /path/to/frp-certs:/certs/frp:ro \
  git.dotnot.pl/karol.kozlowski/appapi-canary:v1.0.0
```

The `HP_*` variables are optional. If `HP_SHARED_KEY` is not set, the container simply runs the Python ExApp without starting the FRP client. If `/certs/frp` exists, the startup script automatically configures TLS for `frpc` using the `client.crt`, `client.key`, and `ca.crt` files in that directory.

### Deployment checklist

- The image must be reachable by the AppAPI Deploy Daemon.
- The ExApp must expose the health endpoint at `/heartbeat` and return `200 {"status":"ok"}`.
- AppAPI expects the daemon to connect to the Unix socket at `/tmp/exapp.sock`.
- For production deployments, prefer a versioned tag like `v1.2.3` instead of floating tags such as `latest`.

Use a versioned tag such as `v1.0.0` rather than `latest` for a stable deployment target.

## Security

This application intentionally has no authentication because it exposes only a fixed health response and no Nextcloud data or administration functions. Do not add sensitive diagnostics, environment output, request headers, or application secrets to its responses.
