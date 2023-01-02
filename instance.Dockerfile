# syntax=docker/dockerfile:1.4

FROM phusion/baseimage:jammy

LABEL org.opencontainers.image.authors="zokradonh <az@zok.xyz>" \
    org.opencontainers.image.title="ARK Survival Evolved Dedicated Server" \
    org.opencontainers.image.description="One container for one ARK instance" \
    org.opencontainers.image.url="https://github.com/zokradonh/ark-server-docker" \
    org.opencontainers.image.source="https://github.com/zokradonh/ark-server-docker"

# install prerequisites
RUN <<EOT
    add-apt-repository multiverse
    apt-get update
    apt-get install -y software-properties-common
    dpkg --add-architecture i386
    apt-get update
    apt-get install -y --no-install-recommends \
        perl-modules \
        curl \
        lsof \
        libc6-i386 \
        lib32gcc1 \
        bzip2 \
        python3 \
        steamcmd
    rm -rf /var/lib/apt/lists/*
EOT

# create steam user
ENV UID=1000 \
    GID=1000
RUN <<EOT
    addgroup --gid $GID steam
    adduser --system --uid $UID --gid $GID --shell /bin/bash steam
EOT

# install arkmanager
RUN curl -sL -o https://git.io/arkmanager | bash -s steam

# install startup script
COPY --chmod=777 startup.sh /etc/rc.local
COPY ark_env.py /scripts

# use phusion's init system
CMD ["/sbin/my_init"]