FROM debian:bookworm-slim

ARG VERSION

# Configure systemd

RUN apt-get update
RUN apt-get dist-upgrade -y
RUN apt-get install -y --no-install-recommends \
        systemd      \
        systemd-sysv \
        cron         \
        anacron

RUN apt-get clean
RUN rm -rf                        \
    /var/lib/apt/lists/*          \
    /var/log/alternatives.log     \
    /var/log/apt/history.log      \
    /var/log/apt/term.log         \
    /var/log/dpkg.log

RUN systemctl mask --   \
    dev-hugepages.mount \
    sys-fs-fuse-connections.mount

RUN rm -f           \
    /etc/machine-id \
    /var/lib/dbus/machine-id

# Configure server

COPY ./simeis-server_${VERSION}.deb .

RUN dpkg -i simeis-server_${VERSION}.deb