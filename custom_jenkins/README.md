# Jenkins Docker-in-Docker Setup

This directory contains the custom Jenkins setup with Docker support.

## Problems

### Problem 1: Docker daemon not accessible
When running `docker build` commands in Jenkins pipelines, you may encounter:
```
ERROR: Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
```

This happens because the Jenkins container has Docker CLI installed but cannot access a Docker daemon.

### Problem 2: Permission denied
After mounting the socket, you might see:
```
ERROR: permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock
```

This happens because the docker group GID inside the container doesn't match the host's docker group GID.

## Solution: Mount Host Docker Socket (Recommended)

The simplest and most common solution is to mount the host's Docker socket into the Jenkins container.

### Using Docker Compose (Recommended)

```bash
cd custom_jenkins
docker-compose up -d --build
```

**Important**: If you're updating the Dockerfile or entrypoint script, rebuild with `--build` flag:
```bash
docker-compose down
docker-compose up -d --build
```

This will:
- Build the custom Jenkins image with the entrypoint script
- Mount the host Docker socket (`/var/run/docker.sock`)
- Automatically fix permissions by matching docker group GID
- Start Jenkins on port 8080

The entrypoint script (`docker-entrypoint.sh`) automatically:
- Detects the host's docker group GID from the mounted socket
- Creates/updates the docker group in the container to match
- Adds the jenkins user to the docker group
- Fixes socket permissions

### Using Docker Run

```bash
docker build -t custom-jenkins .
docker run -d \
  --name jenkins \
  --privileged \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e DOCKER_HOST=unix:///var/run/docker.sock \
  custom-jenkins
```

## Alternative: True Docker-in-Docker (DinD)

If you need true isolation (not recommended for most cases), you can use a DinD sidecar:

```yaml
version: '3.8'
services:
  docker-dind:
    image: docker:dind
    privileged: true
    volumes:
      - docker-certs-ca:/certs/ca
      - docker-certs-client:/certs/client
    environment:
      DOCKER_TLS_CERTDIR: /certs

  jenkins:
    build:
      context: .
      dockerfile: Dockerfile
    depends_on:
      - docker-dind
    environment:
      DOCKER_HOST: tcp://docker-dind:2376
      DOCKER_TLS_CERTDIR: /certs
      DOCKER_CERT_PATH: /certs/client
      DOCKER_TLS_VERIFY: 1
    volumes:
      - jenkins_home:/var/jenkins_home
      - docker-certs-ca:/certs/ca:ro
      - docker-certs-client:/certs/client:ro
```

## Security Note

⚠️ **Warning**: Mounting the Docker socket gives the Jenkins container full access to the host's Docker daemon. This is a security consideration but is the standard approach for CI/CD pipelines.

## Troubleshooting

### Permission Denied After Rebuild

If you still get permission errors after rebuilding:

1. **Check if the container is running with the new image:**
   ```bash
   docker-compose ps
   docker-compose logs jenkins
   ```

2. **Verify the entrypoint script is working:**
   ```bash
   docker-compose exec jenkins ls -la /var/run/docker.sock
   docker-compose exec jenkins groups jenkins
   ```

3. **Manual fix (if needed):**
   ```bash
   # Get the host docker group GID
   stat -c '%g' /var/run/docker.sock
   
   # Then inside the container (as root):
   docker-compose exec -u root jenkins bash
   groupmod -g <HOST_GID> docker
   usermod -aG docker jenkins
   chmod 666 /var/run/docker.sock
   ```

## Verification

After starting Jenkins, verify Docker access:

1. Access Jenkins at `http://localhost:8080`
2. Create a test pipeline or run in Jenkins script console:
   ```groovy
   sh 'docker ps'
   ```

If this works, your Docker setup is correct!

