# End-to-End MLOps Pipeline — Olivetti Face Recognizer

> **MLOps Major Assignment** 
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



## 🤖 Model Details

| Parameter | Value |
|-----------|-------|
| Dataset | Olivetti Faces — 400 images, 40 subjects, 10 images each |
| Image Size | 64×64 pixels (4096 features) |
| Train / Test Split | 70% / 30% (stratified by subject) |
| Algorithm | DecisionTreeClassifier (scikit-learn) |
| Model File | savedmodel.pth (saved using joblib) |
| Test Accuracy | 59.17% |

The Olivetti Faces dataset contains greyscale face images of 40 different subjects. The DecisionTreeClassifier is trained to classify which subject a given image belongs to.

---

## ⚙️ CI/CD Workflow (GitHub Actions)

The CI/CD pipeline is defined in `.github/workflows/ci.yml` and runs automatically on every push.

### Jobs

| Job | Branch Trigger | What it Does |
|-----|---------------|--------------|
| `check_working_repo` | All branches | Sets up Python → installs dependencies → trains model → tests model |
| `build_and_push_docker` | `docker_cicd` only | Logs into Docker Hub → builds image → pushes to Docker Hub |

### GitHub Secrets Required

Go to **GitHub → Settings → Secrets and Variables → Actions** and add:

| Secret Name | Value |
|-------------|-------|
| `DOCKERHUB_USERNAME` | g25ai1035 |
| `DOCKERHUB_TOKEN` | Docker Hub access token |

---

## 🐳 Docker

The application is containerized using a multi-stage Dockerfile. The first stage trains the model and saves it. The second stage copies the saved model and runs the Flask application.

```bash
# Build image
docker build -t g25ai1035/olivetti-face-recognizer:latest .

# Run locally
docker run -d -p 5000:5000 --name face-app g25ai1035/olivetti-face-recognizer:latest

# Push to Docker Hub
docker login
docker push g25ai1035/olivetti-face-recognizer:latest
```

---

## ☸️ Kubernetes Deployment

The app is deployed on Minikube with 3 replicas using a NodePort service on port 30007.


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

3 replicas always running. If a pod is deleted, Kubernetes auto-creates a replacement.

## 🔄 Kubernetes Self-Healing

This project demonstrates Kubernetes **self-healing**, where the desired state of the application is automatically maintained.

* The deployment is configured with **3 replicas**.
* When one pod is manually deleted using:

  ```bash
  kubectl delete pod <POD_NAME>
  ```

  Kubernetes immediately detects that the number of running replicas has dropped below the desired count.
* The Deployment controller automatically creates a **new replacement pod** without any manual intervention.
* The status can be monitored using:

  ```bash
  kubectl get pods -w
  ```
* After a short time, the cluster returns to **3 running pods**, demonstrating Kubernetes' fault tolerance and self-healing capability.

**Workflow:**

```
3 Running Pods
       │
       ▼
Delete One Pod
       │
       ▼
Kubernetes Detects Missing Replica
       │
       ▼
Creates New Pod Automatically
       │
       ▼
3 Running Pods Restored
```


---

## Quick Commands

```bash
# Dev branch
git checkout dev
python3 train.py
python3 test.py

# Docker
docker build -t g25ai1035/olivetti-face-recognizer:latest .
docker push g25ai1035/olivetti-face-recognizer:latest

# Kubernetes
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl get pods
minikube service olivetti-face-recognizer-service --url

# Self healing demo
kubectl delete pod <POD_NAME>
kubectl get pods -w
```
