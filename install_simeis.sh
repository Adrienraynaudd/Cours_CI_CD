#!/bin/bash
set -e

BIN_PATH="./target/release/simeis-server"
INSTALL_BIN_PATH="/usr/bin/simeis-server"
SUPERVISOR_CONF_PATH="./simeis-server.conf"
USER="simeis"

echo "Création de l'utilisateur système $USER..."
if id "$USER" &>/dev/null; then
    echo "L'utilisateur $USER existe déjà."
else
    useradd --system --no-create-home --shell /usr/sbin/nologin $USER
    echo "Utilisateur $USER créé."
fi

echo "Installation du binaire dans $INSTALL_BIN_PATH..."
cp "$BIN_PATH" "$INSTALL_BIN_PATH"
chmod 755 "$INSTALL_BIN_PATH"
chown $USER:$USER "$INSTALL_BIN_PATH"

echo "Installation de la configuration supervisor..."
cat > "$SUPERVISOR_CONF_PATH" <<EOF2
[program:simeis-server]
command=$INSTALL_BIN_PATH
user=$USER
autostart=true
autorestart=true
stderr_logfile=/var/log/simeis-server.err.log
stdout_logfile=/var/log/simeis-server.out.log
EOF2

echo "Création des fichiers de logs si nécessaire..."
mkdir -p /var/log
touch /var/log/simeis-server.err.log /var/log/simeis-server.out.log
chown $USER:$USER /var/log/simeis-server.*.log

echo "Redémarrage de supervisord pour prendre en compte la nouvelle config..."
supervisorctl -c /etc/supervisor/supervisord.conf reread
supervisorctl -c /etc/supervisor/supervisord.conf update

echo "Démarrage du service simeis-server..."
 supervisorctl -c /etc/supervisor/supervisord.conf start simeis-server

echo "Installation terminée. Status du service :"
supervisorctl -c /etc/supervisor/supervisord.conf status simeis-server
