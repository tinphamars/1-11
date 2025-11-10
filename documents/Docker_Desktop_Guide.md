# 🐳 Docker Desktop Quick Start Guide

This short guide helps new team members install, configure, and use **Docker Desktop** effectively.

---

## 1️⃣ Installation

### Windows & macOS
1. Go to [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Download the installer for your OS.
3. Run the installer → follow the on-screen instructions.
4. After installation, open Docker Desktop to verify it runs correctly.

### Linux (Alternative)
Use your distribution’s package manager (e.g., `apt`, `dnf`) or Docker Engine directly.

```bash
# Example for Ubuntu
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io
```

---

## 2️⃣ Configuration

- **Login**: Sign in with your Docker Hub account.
- **Resources (Settings → Resources)**:
  - CPUs: 2–4 cores
  - Memory: 4–8 GB
  - Disk Image Location: choose a drive with enough space
- **File Sharing**: Ensure your project directories are accessible.

---

## 3️⃣ Basic Docker Commands

```bash
# Check Docker version
docker --version

# Verify Docker is running
docker info

# List containers
docker ps -a

# Run a simple container
docker run hello-world

# Stop / remove container
docker stop <container_id>
docker rm <container_id>
```

---

## 4️⃣ Using Docker Compose

To start a multi-container application (e.g., a FastAPI + DB project):

```bash
docker compose up -d --build
```

To stop and remove services:

```bash
docker compose down
```

---

## 5️⃣ Troubleshooting

| Issue | Cause | Solution |
|-------|--------|-----------|
| Docker not starting | WSL 2 or virtualization disabled | Enable virtualization in BIOS / install WSL 2 |
| “Port already in use” | Another service using same port | Stop the other service or change port in compose.yml |
| Container keeps restarting | Misconfiguration or crash loop | Check logs: `docker logs <container_id>` |

---

## 6️⃣ Useful Tips

- Use **Docker Hub** or **GitHub Container Registry** for storing images.
- Regularly clean unused containers/images:
  ```bash
  docker system prune -a
  ```
- Check running containers in Docker Desktop GUI.
- Export and import images:
  ```bash
  docker save myapp:latest -o myapp.tar
  docker load -i myapp.tar
  ```

---

✅ **You’re ready!**  
Once you can start and stop containers, you can move on to working with your team’s RAG Chatbot API project or any other Dockerized application.
