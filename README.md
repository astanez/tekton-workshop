# Tekton Workspace 

Sample apps and Tekton / OpenShift manifests for practicing CI/CD pipelines.

## Contents

| Path | Description |
|------|-------------|
| `src/` | Minimal Flask Python web app |
| `Dockerfile` | UBI 10 (Python 3.12) image for the Python app |
| `openshift/tekton_ws_part1/` | Part 1 workshop resources (ConfigMap, custom Task) |
| `openshift/tekton_ws_part2/` | Part 2: Python app Deployment, Service, Route, pipelines, and GitHub Triggers |
| `spring-boot-pipeline.yml` | Spring Boot Tekton pipeline (clone → s2i-java → Trivy scan → deploy) |

---

## Python web app

A small Flask app that listens on port `8080`.

| Path | Description |
|------|-------------|
| `/` | Greeting message |
| `/health` | Health check for OpenShift probes |

### Project layout

```
src/
  app.py                 # Flask application
  requirements.txt       # Python dependencies
Dockerfile               # registry.access.redhat.com/ubi10/python-312-minimal
openshift/
  tekton_ws_part1/       # Workshop part 1
  tekton_ws_part2/       # Deployment, Service, Route, pipeline
spring-boot-pipeline.yml
```

### Run locally

```bash
cd src
pip install -r requirements.txt
python app.py
```

Open [http://localhost:8080](http://localhost:8080).

### Build and run the container

```bash
podman build -t python-web-app .
podman run --rm -p 8080:8080 python-web-app
```

---

## OpenShift — Part 2 (Python app)

Deploy the app resources, then apply the pipeline:

```bash
oc apply -f openshift/tekton_ws_part2/deployment.yaml
oc apply -f openshift/tekton_ws_part2/service.yaml
oc apply -f openshift/tekton_ws_part2/route.yaml
oc apply -f openshift/tekton_ws_part2/python-app-pipeline.yaml
```

### Pipeline steps (`python-app-pipeline`)

1. **git-clone** — clones the application repository  
2. **buildah** — builds and pushes the image to the internal OpenShift registry  
3. **openshift-client** — updates `deployment/python-web-app` with the new image and waits for rollout  

### Pipeline parameters

| Parameter | Description |
|-----------|-------------|
| `repo-url` | Git repository URL containing this application (required) |
| `image-reference` | Internal image path without tag (defaults to the project’s `python-web-app` image) |
| `dockerfile` | Path to the Dockerfile (default: `./Dockerfile`) |

### Start a PipelineRun

```bash
tkn pipeline start python-app-pipeline \
  -p repo-url=https://github.com/<org>/<repo>.git \
  -w name=shared-data,volumeClaimTemplateFile=<(cat <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
spec:
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 1Gi
EOF
) \
  --use-param-defaults \
  --showlog
```

After a successful run:

```bash
oc get route python-web-app
```

### GitHub webhook (push → pipeline)

To start **`python-app-with-scan-pipeline`** on every push to `main`, see:

[`openshift/tekton_ws_part2/WEBHOOK.md`](openshift/tekton_ws_part2/WEBHOOK.md)

---

## Spring Boot pipeline

`spring-boot-pipeline.yml` defines `spring-boot-withscan-pipeline`:

1. **git-clone** — clones a sample Spring Boot repo  
2. **s2i-java** — builds the image  
3. **trivy-scan** — scans the image for HIGH/CRITICAL vulnerabilities  
4. **openshift-client** — creates/updates `deployment/spring-app` and rolls out the new image  

```bash
oc apply -f spring-boot-pipeline.yml
```

--- ---
