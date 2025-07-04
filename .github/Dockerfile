FROM debian:bookworm-slim

ARG VERSION

COPY ./simeis-server_${VERSION}.deb .

RUN dpkg -i simeis-server_${VERSION}.deb