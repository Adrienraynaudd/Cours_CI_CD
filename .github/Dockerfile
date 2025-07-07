FROM debian:bookworm-slim

EXPOSE 8080

COPY ./artifacts/simeis-server .

RUN chmod +x simeis-server

ENV RUST_LOG="debug"

ENTRYPOINT [ "./simeis-server" ]