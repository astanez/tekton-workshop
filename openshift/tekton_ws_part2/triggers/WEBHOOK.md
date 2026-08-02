# Configure a GitHub webhook for `python-app-with-scan-pipeline`

These Trigger resources start **`python-app-with-scan-pipeline`** when GitHub sends a **push** event to the `main` branch of your repository.

## Prerequisites

- OpenShift Pipelines (Tekton + Triggers) installed on the cluster
- App manifests and the scan pipeline already applied in your project/namespace
- Permission to create webhooks on the GitHub repository

## 1. Apply Trigger resources

From the repository root:

```bash
# Pipeline that the webhook will start
oc apply -f openshift/tekton_ws_part2/python-app-with-scan-pipeline.yaml

# Trigger configuration
oc apply -f openshift/tekton_ws_part2/triggers/triggerbinding.yaml
oc apply -f openshift/tekton_ws_part2/triggers/triggertemplate.yaml
oc apply -f openshift/tekton_ws_part2/triggers/eventlistener.yaml
```

Wait until the EventListener Service exists, then create the Route:

```bash
oc get svc el-python-app-listener
oc apply -f openshift/tekton_ws_part2/triggers/eventlistener-route.yaml
```

## 2. Create the webhook secret

GitHub and the EventListener must share the same secret token.

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

Example:

```text
https://el-python-app-listener-<namespace>.apps.<cluster-domain>/
```

## 4. Configure the GitHub webhook

1. Open the repository on GitHub (e.g. `https://github.com/astanez/tekton-workshop`)
2. Go to **Settings → Webhooks → Add webhook** (or edit an existing one)
3. Fill in:

   | Field | Value |
   |-------|--------|
   | **Payload URL** | The Route URL from step 3 (include `https://`) |
   | **Content type** | **`application/json`** (required — do **not** use `application/x-www-form-urlencoded`) |
   | **Secret** | The same value as `secretToken` in `github-webhook-secret` |
   | **Which events?** | Select **Just the push event** |
   | **Active** | Checked |

4. Click **Add webhook** / **Update webhook**

Then open the webhook → **Recent Deliveries** and confirm a delivery returns **200**.  
A GitHub **ping** may not create a PipelineRun; a real **push** to `main` will.

## 5. Verify

Push a commit to `main`, then:

```bash
oc logs -l eventlistener=python-app-listener -c event-listener --tail=50
tkn pipelinerun list
oc get pipelinerun -l triggered-by=github-push
tkn pipelinerun logs -f -L
```

## How it works

```text
GitHub push (main)
    → HTTPS webhook (Content-Type: application/json)
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

```bash
oc apply -f openshift/tekton_ws_part2/triggers/eventlistener.yaml
```

## Troubleshooting

### Errors you may see in EventListener logs

| Log message | Cause | Fix |
|-------------|--------|-----|
| `invalid character 'p' looking for beginning of value` | Webhook **Content type** is `application/x-www-form-urlencoded` (body starts with `payload=...`) | In GitHub webhook settings set **Content type** to **`application/json`**, then **Redeliver** the failed delivery |
| `unexpected end of JSON input` | Empty body — often a browser GET, route probe, or incomplete request | Harmless if not from GitHub. In GitHub **Recent Deliveries**, confirm the request has a JSON body. Do not open the Route URL in a browser to “test” it |
| Delivery OK / 200 but no PipelineRun | Secret mismatch, event not `push`, or branch not `main` | Match secrets; push to `main`; check interceptor filter in logs |

### Checklist after fixing content type

1. GitHub → webhook → set **Content type** = `application/json` → **Update webhook**
2. **Recent Deliveries** → pick a failed push → **Redeliver**
3. Confirm response is **200**
4. Check: `oc get pipelinerun -l triggered-by=github-push`

### Other issues

| Symptom | What to check |
|---------|----------------|
| GitHub delivery failed (timeout / 5xx) | Route URL, TLS, EventListener pod: `oc get pods -l eventlistener=python-app-listener` |
| PipelineRun created but fails | SA permissions, PVC, image pull, Trivy HIGH/CRITICAL findings |
| `el-python-app-listener` Service missing | `oc describe eventlistener python-app-listener` |
