# Docker Episode 4 – Port Mapping with a FastAPI App

A small demo showing how **ports work in Docker**: how a web app running *inside* a container is reached from your *host* machine using `EXPOSE` and the `-p` (publish) flag.

## What this episode covers

A container is an isolated environment with its own network. If an app listens on port `8000` inside the container, your browser on the host **cannot** reach it automatically. You have to map a host port to the container port:

```
Browser  ──►  localhost:<HOST_PORT>  ──►  Docker  ──►  container:<CONTAINER_PORT>
```

Key ideas:

| Concept | Meaning |
|---|---|
| `EXPOSE 8000` (Dockerfile) | Documentation only. Says "this container listens on 8000". It does **not** open the port to the host. |
| `-p 8000:8000` (docker run) | Actually publishes the port. Format is `HOST_PORT:CONTAINER_PORT`. |
| `--host 0.0.0.0` (uvicorn) | The app must listen on all interfaces. If it binds to `127.0.0.1`, it is only reachable from inside the container, and port mapping will not work. |
| Different host port | You can map any free host port to the container's 8000, e.g. `-p 9000:8000`. |

## Project files

| File | Purpose |
|---|---|
| `main.py` | FastAPI app with one route, `GET /`, returning a JSON message. |
| `Dockerfile` | Builds the image: Python 3.12-slim, installs FastAPI + Uvicorn, copies `main.py`, exposes 8000, starts Uvicorn. |

### main.py

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hellow from Docker Episode 4 "}
```

### Dockerfile (line by line)

```dockerfile
FROM python:3.12-slim                 # small Python base image
WORKDIR /app                          # working directory inside the container
RUN pip install fastapi uvicorn       # install dependencies at build time
COPY main.py .                        # copy the app into /app
EXPOSE 8000                           # document the port the app listens on
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Prerequisites

- Docker Desktop installed and running (`docker --version` to check)

## Demo – commands used

### 1. Build the image

```bash
docker build -t docker-port-demo .
```

### 2. Run the container with port mapping

```bash
docker run -d -p 8000:8000 --name port-demo docker-port-demo
```

- `-d` runs in the background
- `-p 8000:8000` maps host port 8000 to container port 8000
- `--name` gives the container a friendly name

### 3. Test it

Open <http://localhost:8000> in a browser, or:

```bash
curl http://localhost:8000
```

Expected output:

```json
{"message":"Hellow from Docker Episode 4 "}
```

FastAPI also gives you interactive docs at <http://localhost:8000/docs>.

### 4. Map to a different host port

The container still listens on 8000 inside; only the host side changes.

```bash
docker run -d -p 9000:8000 --name port-demo-9000 docker-port-demo
curl http://localhost:9000
```

You can run several copies of the same image side by side on different host ports:

```bash
docker run -d -p 8001:8000 --name app1 docker-port-demo
docker run -d -p 8002:8000 --name app2 docker-port-demo
```

### 5. What happens without `-p`?

```bash
docker run -d --name no-port docker-port-demo
curl http://localhost:8000      # fails: connection refused / nothing listening
```

`EXPOSE` alone does not publish anything. Use `-p`, or `-P` to publish all exposed ports to random host ports:

```bash
docker run -d -P --name random-port docker-port-demo
docker ps                       # see which host port was assigned
```

### 6. Inspect and debug

```bash
docker ps                       # running containers and their port mappings
docker port port-demo           # show port mapping for one container
docker logs port-demo           # app output (Uvicorn logs)
docker logs -f port-demo        # follow logs live
docker exec -it port-demo bash  # shell inside the container
docker images                   # list images
```

### 7. Stop and clean up

```bash
docker stop port-demo
docker rm port-demo
# or remove everything from this demo
docker rm -f port-demo port-demo-9000 app1 app2 no-port random-port
docker rmi docker-port-demo
```

## Common problems

| Problem | Cause / fix |
|---|---|
| `port is already allocated` | Host port is in use. Pick another one: `-p 8080:8000`. |
| Page doesn't load, container is running | App is bound to `127.0.0.1`. Use `--host 0.0.0.0` in the `CMD`. |
| Works inside container but not from host | Missing `-p` flag. |
| Changed `main.py` but nothing changed | Rebuild the image: `docker build -t docker-port-demo .` |

## Summary

- The app listens on **8000 inside** the container.
- `EXPOSE` documents it; **`-p HOST:CONTAINER` publishes it**.
- The app must bind to `0.0.0.0`.
- Host and container ports can differ, which lets you run many containers of the same image at once.
