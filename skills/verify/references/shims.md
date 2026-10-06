# A missing service is a rung, not a wall

Read this when a flow is unreachable because an external service is absent.

"Could not verify" is an honest floor, not the first answer. Between "it works" and "I could not reach it" there is a rung worth trying: the flow is usually unreachable because one external service is missing, and a service that speaks a documented wire protocol can be stood up locally.

Prefer that to mocking the app's own code. A mock proves your mock works. A shim leaves the real client, the real retries and the real server logic executing.

## The ladder

Work down it and stop at the first rung that runs. Say in the evidence file which rung you reached.

1. **A published shim for that exact service.** Someone tested it against the real API. See the table.
2. **A mock generated from the vendor's OpenAPI spec.** `npx @stoplight/prism-cli mock <spec-url> -p 4010`. Find the spec in the APIs.guru index (`curl -s https://api.apis.guru/v2/list.json`, keyed by vendor domain, use `versions[preferred].swaggerUrl`) or in the vendor's own repo. Prism replays the spec's example verbatim, and vendor examples are often error payloads. It has no state and no logic. So assert on the request your app sent, not on the body it got back.
3. **A shim you write**, speaking the same wire protocol. Only after 1 and 2 both failed, and say so.
4. **"Could not reach the flow."** The honest floor, with which rung broke and why.

## The table

| The flow needs | Shim | Run it |
|---|---|---|
| S3, object storage, presigned URLs | MinIO | `minio server /tmp/s3` on :9000, keys `minioadmin`/`minioadmin` |
| Outbound email, SMTP | Mailpit | SMTP on :1025, a JSON API on :8025 that tells you what the app sent |
| Stripe | stripe-mock | serves the real Stripe OpenAPI on :12111; the Node SDK has no env var, pass `{host:'localhost', port:12111, protocol:'http'}` |
| Google Cloud Storage | fake-gcs-server | vendor release tarball |
| Azure Blob | azurite | `npx azurite --location /tmp/az` |
| OAuth 2 or OIDC sign-in | oauth2-mock-server | `npx oauth2-mock-server -p 8080`, real signed JWTs against a real JWKS endpoint |
| Redis, a cache, a rate limiter | a local Redis | `redis-server` |
| Postgres | a local Postgres | a fresh database per run |
| Anything else with an OpenAPI spec | Prism | rung 2 above |

Pick binaries for the box's own architecture. Check whether the box has Docker before you pick a shim that only ships as a container image. Check the box's npm policy (a minimum release age or `ignore-scripts`) before you pick a package that needs a postinstall.

## Two rules if you do it

- **Point the app at the shim with an environment variable or a base-URL setting.** Never edit the app to make the flow reachable. That verifies something nobody is shipping. If the app hardcodes the vendor URL with no override, that is a finding worth reporting, not a licence to edit it.
- **Label it in the evidence file.** Which calls were real, which were shimmed, and which rung the shim came from.
