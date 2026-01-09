# Use the Jenkins image as the base image
FROM jenkins/jenkins:lts

# Switch to root user to install dependencies
USER root

# Install prerequisites and Docker
RUN apt-get update -y && \
apt-get install -y apt-transport-https ca-certificates curl gnupg && \
install -m 0755 -d /etc/apt/keyrings && \
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
chmod a+r /etc/apt/keyrings/docker.gpg && \
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update -y && \
    apt-get install -y docker-ce docker-ce-cli containerd.io && \
    apt-get clean

# Copy the entrypoint script that will fix Docker socket permissions
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Add Jenkins user to the Docker group (will be adjusted at runtime if needed)
RUN groupadd -f docker && \
    usermod -aG docker jenkins

# Set the entrypoint (will run as root initially to fix permissions)
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Note: We stay as root here because the entrypoint needs root to fix permissions
# The Jenkins entrypoint script will switch to jenkins user automatically