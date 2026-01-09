#!/bin/bash
set -e

# Only run this if we're root (which we should be at container start)
if [ "$(id -u)" = "0" ]; then
    # Get the GID of the docker group from the mounted socket
    if [ -e /var/run/docker.sock ]; then
        DOCKER_GID=$(stat -c '%g' /var/run/docker.sock 2>/dev/null || echo "")
        
        if [ -n "$DOCKER_GID" ] && [ "$DOCKER_GID" != "0" ]; then
            # Check if docker group exists and has the correct GID
            EXISTING_GID=$(getent group docker | cut -d: -f3 2>/dev/null || echo "")
            
            if [ "$EXISTING_GID" != "$DOCKER_GID" ]; then
                # Remove existing docker group if it has wrong GID
                groupdel docker 2>/dev/null || true
                
                # Create docker group with the correct GID from host
                groupadd -g $DOCKER_GID docker 2>/dev/null || true
            fi
            
            # Add jenkins user to docker group
            usermod -aG docker jenkins 2>/dev/null || true
        fi
        
        # Fix permissions on the socket (make it accessible to docker group)
        chmod 666 /var/run/docker.sock 2>/dev/null || chgrp docker /var/run/docker.sock 2>/dev/null || true
    fi
fi

# Execute the original Jenkins entrypoint (it will handle user switching)
exec /usr/local/bin/jenkins.sh "$@"

