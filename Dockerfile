FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        fortune-mod \
        cowsay \
        netcat-openbsd \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/games/cowsay /usr/local/bin/cowsay \
    && ln -sf /usr/games/fortune /usr/local/bin/fortune

WORKDIR /app

COPY wisecow.sh .
RUN chmod +x wisecow.sh \
    && useradd -r -u 10001 -s /usr/sbin/nologin wisecow \
    && chown -R wisecow:wisecow /app

USER wisecow

EXPOSE 4499

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD nc -z 127.0.0.1 4499 || exit 1

CMD ["./wisecow.sh"]
