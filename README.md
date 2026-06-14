# End-to-End MLOps Pipeline — Olivetti Face Recognizer

> **MLOps Major Assignment** | PGD May 2026  
> Dataset: Olivetti Faces (sklearn) | Model: DecisionTreeClassifier

---

## Repository Links

| Resource | URL |
|----------|-----|
| **GitHub Repository** | `https://github.com/priyanships31/mlops-major-project` |
| **Docker Hub Image**  | `https://hub.docker.com/r/g25ai1035/olivetti-face-recognizer` |

---

## Project Structure

```
mlops-major/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI/CD pipeline
├── k8s/
│   ├── deployment.yaml         # Kubernetes Deployment (3 replicas)
│   └── service.yaml            # Kubernetes NodePort Service
├── templates/
│   └── index.html              # Flask UI template
├── train.py                    # Train & save DecisionTreeClassifier
├── test.py                     # Evaluate saved model accuracy
├── app.py                      # Flask web application
├── Dockerfile                  # Multi-stage Docker build
├── requirements.txt            # Python dependencies
├── .gitignore
└── README.md
```

---

## Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Initial repo setup only |
| `dev` | Model development + CI job (`check_working_repo`) |
| `docker_cicd` | Docker build, push & Kubernetes deployment |

> Neither `dev` nor `docker_cicd` is merged back into `main` (per assignment spec).

---

## Step-by-Step Setup

### Step 1 — Clone & Branch Setup

```bash
# Clone the repository
git clone https://github.com/priyanships31/mlops-major-project.git
cd mlops-major

# Verify branches
git branch -a
```

### Step 2 — Dev Branch: Model Training & Testing

```bash
git checkout dev

# Install dependencies
pip install -r requirements.txt

# Train the model → produces savedmodel.pth
python train.py

# Evaluate the model → prints test accuracy
python test.py
```

Expected output from `test.py`:
```
=============================================
  Test Accuracy : ~65–75%
=============================================
```

### Step 3 — Docker Branch: Build & Run Locally

```bash
git checkout docker_cicd

# Build Docker image
docker build -t olivetti-face-recognizer:latest .

# Run container
docker run -d -p 5000:5000 --name face-app olivetti-face-recognizer:latest

# Verify health endpoint
curl http://localhost:5000/health

# Open browser → http://localhost:5000
```

### Step 4 — Push to Docker Hub

```bash
docker login

docker tag olivetti-face-recognizer:latest \
  g25ai1035/olivetti-face-recognizer:latest

docker push g25ai1035/olivetti-face-recognizer:latest
```

### Step 5 — Kubernetes Deployment

#### 5a. Update image name in deployment.yaml

Edit `k8s/deployment.yaml` and replace `YOUR_DOCKERHUB_USERNAME` with your actual username.

#### 5b. Apply manifests

```bash
# Apply Deployment (3 replicas)
kubectl apply -f k8s/deployment.yaml

# Apply NodePort Service
kubectl apply -f k8s/service.yaml

# Verify pods are running
kubectl get pods
```

Expected output:
```
NAME                                        READY   STATUS    RESTARTS   AGE
olivetti-face-recognizer-xxxxxxxxx-aaaaa    1/1     Running   0          30s
olivetti-face-recognizer-xxxxxxxxx-bbbbb    1/1     Running   0          30s
olivetti-face-recognizer-xxxxxxxxx-ccccc    1/1     Running   0          30s
```

#### 5c. Access the app

```bash
# Get Node IP (for local cluster use localhost or minikube ip)
minikube ip      # e.g. 192.168.49.2

# Open in browser
http://<NODE_IP>:30007
```

#### 5d. Demonstrate self-healing (destroy a pod)

```bash
# List pods
kubectl get pods

# Delete one pod — Kubernetes automatically recreates it
kubectl delete pod <POD_NAME>

# Watch the replacement spin up immediately
kubectl get pods -w
```

You will see the pod count stay at 3 as a new pod is scheduled.

---

## CI/CD Workflow (GitHub Actions)

### Secrets Required

Add these in **GitHub → Settings → Secrets and Variables → Actions**:

| Secret Name | Value |
|-------------|-------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token (not password) |

### Jobs

| Job | Branch Trigger | What it Does |
|-----|---------------|--------------|
| `check_working_repo` | All branches | Installs deps → trains model → tests model |
| `build_and_push_docker` | `docker_cicd` only | Builds Docker image → pushes to Docker Hub |

---

## Model Details

| Parameter | Value |
|-----------|-------|
| Dataset | Olivetti Faces (400 samples, 40 subjects) |
| Features | 4096 (64×64 flattened pixels) |
| Train / Test Split | 70% / 30% (stratified) |
| Algorithm | DecisionTreeClassifier |
| Serialisation | joblib (savedmodel.pth) |

---

## Flask API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI for image upload |
| `/predict` | POST | Accepts `multipart/form-data` with `image` field; returns JSON prediction |
| `/health` | GET | Health check — returns `{"status": "healthy"}` |

### Example `/predict` response

```json
{
  "predicted_class": 12,
  "confidence": "82.35%",
  "message": "Predicted Subject ID: 12"
}
```

---

## Kubernetes Architecture

```
Internet
    │
    ▼
NodePort :30007
    │
    ▼
Service (ClusterIP :80)
    │
    ├─── Pod 1 (Flask :5000)
    ├─── Pod 2 (Flask :5000)
    └─── Pod 3 (Flask :5000)
          └── savedmodel.pth (baked into image)
```

The Deployment spec sets `replicas: 3`. If any pod is deleted or crashes, the ReplicaSet controller automatically schedules a replacement, maintaining exactly 3 running instances at all times.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `savedmodel.pth not found` | Run `python train.py` first |
| Docker build fails on model step | Ensure Python deps install correctly in the builder stage |
| Kubernetes pods in `ImagePullBackOff` | Check that the image name in `deployment.yaml` matches your Docker Hub repo |
| NodePort not reachable | Run `minikube service olivetti-face-recognizer-service --url` for the correct URL |
