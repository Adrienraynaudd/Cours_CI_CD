FROM debian:bookworm-slim

EXPOSE 8080

COPY ./artifacts/simeis-server_AMP .

RUN chmod +x simeis-server_AMP

ENV RUST_LOG="debug"

ENTRYPOINT [ "./simeis-server_AMP" ]