#!/bin/bash

set -e

sudo useradd --system --no-create-home --shell /usr/sbin/nologin simeis || echo "✅ Utilisateur déjà existant"

sudo install -m 755 ./target/release/simeis-server /usr/bin/simeis-server
sudo chown root:root /usr/bin/simeis-server

sudo install -Dm644 ./docs/simeis-server /usr/share/man/man1/simeis-server
sudo gzip -f /usr/share/man/man1/simeis-server

sudo install -Dm644 ./supervisor/simeis-server.conf /etc/supervisor/conf.d/simeis-server.conf

sudo supervisorctl reread
sudo supervisorctl update

sudo supervisorctl start simeis-server

sudo supervisorctl status simeis-server