# Hashview Server and Agent Deployment on Linode Kubernetes Engine

This guide provides step-by-step instructions to deploy the Hashview server and Hashview agents on the Linode Kubernetes Engine (LKE) using Docker and Kubernetes for horizontal scaling.

## Prerequisites

- A Linode account with access to Linode Kubernetes Engine (LKE).
- `kubectl` configured to connect to your LKE cluster.
- Docker installed on your local machine.
- Linode CLI or Terraform (optional for automated infrastructure setup).
- Hashview agent tarball (`hashview-agent.<version>.tgz`) available locally.

## Table of Contents

1. [Hashview Server Installation](#hashview-server-installation)
2. [Hashview Agent Dockerfile](#hashview-agent-dockerfile)
3. [Build and Push Docker Image](#build-and-push-docker-image)
4. [Kubernetes Deployment Configuration](#kubernetes-deployment-configuration)
5. [Horizontal Pod Autoscaler](#horizontal-pod-autoscaler)
6. [Final Steps](#final-steps)

## Hashview Server Installation

### Step 1: Set Up MySQL

1. Update the package list and install MySQL server:
   ```bash
   sudo apt update
   sudo apt install mysql-server
   ```

2. Start MySQL service and secure the installation:

  ```bash
  sudo service mysql start
  sudo mysql_secure_installation
  ```
3. Log into MySQL and create a database and user for Hashview:

```bash
sudo mysql
CREATE USER 'hashview'@'localhost' IDENTIFIED BY 'DONTUSETHISPASSWORD!';
GRANT ALL PRIVILEGES ON hashview.* TO 'hashview'@'localhost';
FLUSH PRIVILEGES;
CREATE DATABASE hashview;
exit
```

## Step 2: Install Hashview Server

1.Install required dependencies:

```bash
sudo apt-get install python3 python3-pip python3-flask
```

2. Clone the Hashview repository and install dependencies:

```bash
git clone https://github.com/hashview/hashview
cd hashview
pip3 install -r requirements.txt
```

3. Run the setup and start the server:

```bash
./setup.py
./hashview.py
```
4. Access Hashview at https://your-server-ip:8443 (self-signed certificate warning expected unless using something else like letsencrypt).

## Hashview Agent Dockerfile

1. Create a Dockerfile with the following content: (Available in this git directory)

```dockerfile

FROM debian:latest

RUN apt-get update && \
    apt-get install -y python3 python3-pip wget tar && \
    apt-get clean

WORKDIR /opt/hashview
#this should be able to be downloaded from your server
COPY hashview-agent.<version>.tgz /opt/hashview/

RUN tar -xzvf hashview-agent.<version>.tgz && \
    cp -r hashview-agent/* .

RUN pip3 install -r requirements.txt

CMD ["python3", "./hashview-agent.py"]
```

Replace hashview-agent.<version>.tgz with your specific version file name downloaded from your server

## Build and Push Docker Image

1. Build the Docker image:

```bash
docker build -t yourusername/hashview-agent:latest .
```
2.  *Push the image to Docker Hub: (not required but here incase)*

```bash
docker push yourusername/hashview-agent:latest
```

## Kubernetes Deployment Configuration

1. Create a Kubernetes deployment configuration file hashview-agent-deployment.yaml:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hashview-agent
  labels:
    app: hashview-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: hashview-agent
  template:
    metadata:
      labels:
        app: hashview-agent
    spec:
      containers:
      - name: hashview-agent
        image: yourusername/hashview-agent:latest
        imagePullPolicy: Always
        resources:
          limits:
            cpu: "0.5" #Modify variable values where required
            memory: "512Mi"
          requests:
            cpu: "0.1"
            memory: "256Mi"
        env:
        - name: HASHVIEW_SERVER_URL
          value: "https://hash.server-url"
        - name: HASHVIEW_SERVER_TOKEN
          value: "TOKEN HERE"
```

2. Apply the configuration to your Kubernetes cluster:

```bash
kubectl apply -f hashview-agent-deployment.yaml
```
4. Verify the deployment:

```bash
kubectl get pods -l app=hashview-agent
```
## Horizontal Pod Autoscaler

1. Create an autoscaler configuration file hashview-agent-hpa.yaml:

```yaml
apiVersion: autoscaling/v2beta2
kind: HorizontalPodAutoscaler
metadata:
  name: hashview-agent-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: hashview-agent
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

2. Apply the HPA configuration:

```bash
kubectl apply -f hashview-agent-hpa.yaml
```

3. Check the autoscaler status:

```bash
kubectl get hpa
```
