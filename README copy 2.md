# Tekton Workspace

Sample apps and Tekton / OpenShift manifests for practicing CI/CD pipelines.

## Contents

| Path | Description |
|------|-------------|
| `openshift/tekton_ws_part1/` | Workshop Part 1: custom Task and ConfigMap |
| `src/` | Minimal Flask Python web app (Part 2) |
| `Dockerfile` | UBI 10 (Python 3.12) image for the Python app |
| `openshift/tekton_ws_part2/` | Workshop Part 2: Deployment, Service, Route, pipelines, and GitHub Triggers |

---

## Workshop Part 1 — Create your own first Task

**Objective:** learn how to author a custom Tekton Task and run it on OpenShift.

This part showcases:

| Concept | What you practice |
|---------|-------------------|
| **Parameters** | Pass input into a Task and use `$(params…)` in a step |
| **ConfigMap** | Mount a ConfigMap into a step and print its contents |
| **Exchange data between steps** | Write from one step to a workspace, read it in a later step |

### Resources

| File | Description |
|------|-------------|
| `openshift/tekton_ws_part1/project_confmap.yaml` | Sample project request and ConfigMap `tkn-workshop-config` |
| `openshift/tekton_ws_part1/my_test_task.yaml` | Custom Task `my-test-task` |

### What the Task does

`my-test-task` runs four steps:

1. **read-variable** — reads the `hello-text` parameter and prints it  
2. **read-configmap** — mounts ConfigMap `tkn-workshop-config` and prints its keys/values  
3. **write-to-storage** — writes a message (using the parameter) into the `my-ws` workspace  
4. **read-from-storage** — reads that file back from the workspace (data shared across steps)

### Proceed in following steps

1. Apply the task
2. Analyse the task config. Understand the variables, volumes, workspaces, 
3. Start to create a pipelinge for this taks. Take a look at pipeline workspaces. Understand all shared-workspaces options 
4. Observe the logs, pvs, pv, created containers 
5. Take a look at PipeLineRun config.  




## Workshop Part 2 — Building a Tekton Pipeline for a Python app

**Objective:** build and deploy the Python app with Tekton (clone → build → deploy), then optionally add scanning and GitHub Triggers.

### Python web app

Used in **Workshop Part 2**. A small Flask app on port `8080` with a dark-blue Tekton / OpenShift landing page.

### Layout

```
src/
  app.py                 # Flask application
  requirements.txt       # Python dependencies (Flask)
  templates/
    index.html           # Landing page
  static/
    style.css            # Page styles
Dockerfile               # registry.access.redhat.com/ubi10/python-312-minimal
```

### Run locally

```bash
cd src
pip install -r requirements.txt
python app.py
```

Open [http://localhost:8080](http://localhost:8080).

### Build and run the container

From the repository root (where the `Dockerfile` lives):

```bash
podman build -t python-web-app .
podman run --rm -p 8080:8080 python-web-app
```

---

## Workshop Part 2 — Building a Tekton Pipeline for the Python app


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
| `repo-url` | Git repository URL containing this application |
| `image-reference` | Internal image path without tag (defaults to the project’s `python-web-app` image) |
| `dockerfile` | Path to the Dockerfile (default: `./Dockerfile`) |

### GitHub webhook (push → pipeline)

To start **`python-app-with-scan-pipeline`** on every push to `main`, see:

[`openshift/tekton_ws_part2/triggers/WEBHOOK.md`](openshift/tekton_ws_part2/triggers/WEBHOOK.md)
