# Configure a GitHub webhook for `python-app-with-scan-pipeline`

These Trigger resources start **`python-app-with-scan-pipeline`** when GitHub sends a **push** event to the `main` branch of your repository.

## Prerequisites

- OpenShift Pipelines (Tekton + Triggers) installed on the cluster
- App manifests and the scan pipeline already applied in your project/namespace
- Permission to create webhooks on the GitHub repository

## 1. Apply Trigger resources

From the repository root (or with paths adjusted to your checkout):

```bash
# Pipeline that the webhook will start
oc apply -f openshift/tekton_ws_part2/python-app-with-scan-pipeline.yaml

# Trigger configuration
oc apply -f openshift/tekton_ws_part2/triggerbinding.yaml
oc apply -f openshift/tekton_ws_part2/triggertemplate.yaml
oc apply -f openshift/tekton_ws_part2/eventlistener.yaml
```

Wait until the EventListener Service exists, then create the Route:

```bash
oc get svc el-python-app-listener
oc apply -f openshift/tekton_ws_part2/eventlistener-route.yaml
```

## 2. Create the webhook secret

GitHub and the EventListener must share the same secret token.

Pick a strong random value (example only):

```bash
export WEBHOOK_SECRET="$(openssl rand -hex 20)"
echo "Save this secret for GitHub: $WEBHOOK_SECRET"

oc create secret generic github-webhook-secret \
  --from-literal=secretToken="$WEBHOOK_SECRET"
```

If the secret already exists and you need to rotate it:

```bash
oc delete secret github-webhook-secret
oc create secret generic github-webhook-secret \
  --from-literal=secretToken="$WEBHOOK_SECRET"
```

## 3. Get the webhook URL

```bash
oc get route el-python-app-listener \
  -o jsonpath='https://{.spec.host}{"\n"}'
```

The EventListener endpoint is that host (root path `/`). Example:

```text
https://el-python-app-listener-<namespace>.apps.<cluster-domain>/
```

## 4. Configure the GitHub webhook

1. Open the repository on GitHub:  
   `https://github.com/astanez/tekton-workshop`
2. Go to **Settings → Webhooks → Add webhook**
3. Fill in:

   | Field | Value |
   |-------|--------|
   | **Payload URL** | The Route URL from step 3 (include `https://`) |
   | **Content type** | `application/json` |
   | **Secret** | The same value as `secretToken` in `github-webhook-secret` |
   | **Which events?** | Select **Just the push event** |
   | **Active** | Checked |

4. Click **Add webhook**

GitHub will send a ping (and later push deliveries). A ping may not start a PipelineRun; a real push to `main` will.

## 5. Verify

Push a commit to `main`, then:

```bash
# EventListener logs
oc logs -l eventlistener=python-app-listener -c event-listener --tail=50

# New PipelineRuns
tkn pipelinerun list
# or
oc get pipelinerun -l triggered-by=github-push
```

Watch the latest run:

```bash
tkn pipelinerun logs -f -L
```

## How it works

```text
GitHub push (main)
    → HTTPS webhook
    → OpenShift Route (el-python-app-listener)
    → EventListener (validates secret, filters push + main)
    → TriggerBinding (repo URL + commit)
    → TriggerTemplate
    → PipelineRun (python-app-with-scan-pipeline)
```

## Optional: another branch

The CEL filter currently allows only `refs/heads/main`. To use `develop` instead, edit `eventlistener.yaml`:

```yaml
value: "body.ref == 'refs/heads/develop'"
```

Re-apply:

```bash
oc apply -f openshift/tekton_ws_part2/eventlistener.yaml
```

## Troubleshooting

| Symptom | What to check |
|---------|----------------|
| GitHub shows delivery failed | Route URL, TLS, and that the EventListener pod is running (`oc get pods -l eventlistener=python-app-listener`) |
| Delivery OK but no PipelineRun | Secret mismatch; event not `push`; branch not `main`; check EventListener logs |
| PipelineRun created but fails | Same as a manual run: SA permissions, PVC, image pull, Trivy findings |
| `el-python-app-listener` Service missing | EventListener not ready — check `oc describe eventlistener python-app-listener` |
