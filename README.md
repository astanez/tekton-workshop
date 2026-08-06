# Tekton Intro Workshop

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

**Objective:** learn how to write a custom Tekton Task and run it on OpenShift.

### Workshop Part 1 Content

This part showcases:

| Concept | What you practice |
|---------|-------------------|
| **Parameters** | Pass input into a Task and use `$(params…)` in a step |
| **ConfigMap** | Mount a ConfigMap into a step and print its contents |
| **Exchange data between steps** | Write from one step to a workspace, read it in a later step |

#### Resources

| File | Description |
|------|-------------|
| `project_confmap.yaml` | Sample project request and ConfigMap `tkn-workshop-config` |
| `tasks/print_env_var.yaml` | Print step environment variables |
| `tasks/print_param_volume.yaml` | Use a Task parameter and read a mounted ConfigMap |
| `tasks/read_write_workspaces.yaml` | Write in one step, read in another via a workspace |
| `tasks/task_with_4_steps.yaml` | Combined Task: params + ConfigMap + workspace exchange |
| `PipelineRun.yaml` | Example PipelineRun with a PVC-backed workspace |
| `telton_pruner.yaml` | Example pruner config for old PipelineRuns |

#### What `task-with-4-steps` does

`task-with-4-steps` runs four steps:

1. **read-variable** — reads the `hello-text` parameter and prints it  
2. **read-configmap** — mounts ConfigMap `tkn-workshop-config` and prints its keys/values  
3. **write-to-storage** — writes a message (using the parameter) into the `my-ws` workspace  
4. **read-from-storage** — reads that file back from the workspace (data shared across steps)

### Proceed in following steps

1. Create project and ConfigMap by applying project_confmap.yaml 
2. Create tasks by applying configs from tasks/
2. Analyse the task config. Understand the variables, volumes, workspaces, 
3. Create an run pipelins for these taks. Take a look at pipeline workspaces. Understand all shared-workspaces options.  
4. Observe the pvs, pv, pods, containers and logs
5. Take a look at PipeLineRun config.  


---

## Workshop Part 2 — Building a Tekton Pipeline for a Python app

**Objective:** build and deploy the Python app with Tekton (clone → build → deploy), then optionally add scanning and GitHub Triggers.

### Python web app

Used in **Workshop Part 2**. A small Flask app on port `8080` with a dark-blue Tekton / OpenShift landing page.

#### Layout

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

#### How to run locally

```bash
cd src
pip install -r requirements.txt
python app.py
```

Open [http://localhost:8080](http://localhost:8080).

#### How to build and run the container locally

From the repository root (where the `Dockerfile` lives):

```bash
podman build -t python-web-app .
podman run --rm -p 8080:8080 python-web-app
```


### Workshop Part 2 — Process in following steps


#### 1. Deploy the app resources via Web Console or via CLI, then apply the pipeline:

```bash
oc apply -f openshift/tekton_ws_part2/deployment.yaml
oc apply -f openshift/tekton_ws_part2/service.yaml
oc apply -f openshift/tekton_ws_part2/route.yaml
oc apply -f openshift/tekton_ws_part2/python-app-pipeline.yaml
```

#### 2. Look at Pipeline tasks (`python-app-pipeline`)

a. **git-clone** — clones the application repository  
b. **buildah** — builds and pushes the image to the internal OpenShift registry  
c. **openshift-client** — updates `deployment/python-web-app` with the new image and waits for rollout  

#### Look at Pipeline parameters

| Parameter | Description |
|-----------|-------------|
| `repo-url` | Git repository URL containing this application |
| `image-reference` | Internal image path without tag (defaults to the project’s `python-web-app` image) |
| `dockerfile` | Path to the Dockerfile (default: `./Dockerfile`) |


#### 3. Run Pipeline (`python-app-pipeline`)

Observe logs and created containers. Run the app in the browser. 


#### 4. Apply Pipeline (`python-app-with-scan-pipeline`)

```bash
oc apply -f openshift/tekton_ws_part2/python-app-with-scan-pipeline.yaml
```

#### 5. Run Pipeline (`python-app-with-scan-pipeline`)

Observe logs and created containers. Notice there is a vulnerability scan task. ‚
Run the app in the browser. 

#### 6. Configure GitHub webhook for python-app-with-scan-pipeline (push → pipeline)

To start **`python-app-with-scan-pipeline`** on every push to `main`, see the guide:

[`openshift/tekton_ws_part2/triggers/WEBHOOK.md`](openshift/tekton_ws_part2/triggers/WEBHOOK.md)


#### 6. Make changes in the app. Commit and push. 

See if the PipelineRun was startet. Observe it. 
Run the app in the browser and see the changes. 

---