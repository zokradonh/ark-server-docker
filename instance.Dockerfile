# syntax=docker/dockerfile:1.4

FROM phusion/baseimage:jammy-1.0.1

LABEL org.opencontainers.image.authors="zokradonh <az@zok.xyz>" \
    org.opencontainers.image.title="ARK Survival Evolved Dedicated Server" \
    org.opencontainers.image.description="One container for one ARK instance" \
    org.opencontainers.image.url="https://github.com/zokradonh/ark-server-docker" \
    org.opencontainers.image.source="https://github.com/zokradonh/ark-server-docker"

# install prerequisites
RUN <<EOT
    echo steam steam/question select "I AGREE" | debconf-set-selections
    echo steam steam/license note '' | debconf-set-selections
    add-apt-repository multiverse
    dpkg --add-architecture i386
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        perl-modules \
        curl \
        lsof \
        libc6-i386 \
        lib32gcc-s1 \
        bzip2 \
        python3 \
        steamcmd
    rm -rf /var/lib/apt/lists/*
    ln -sf /usr/games/steamcmd /usr/bin/steamcmd
EOT

# create steam user
ENV UID=1000 \
    GID=1000
RUN <<EOT
    addgroup --gid $GID steam
    adduser --system --uid $UID --gid $GID --shell /bin/bash steam
EOT

# install arkmanager
RUN curl -sL https://git.io/arkmanager | bash -s steam

# install startup script
COPY --chmod=777 startup.sh /etc/rc.local
COPY --chmod=777 scripts/* /scripts/
COPY arkmanager-docker.cfg /etc/arkmanager/

COPY --chmod=777 /scripts/update.sh /usr/bin/update

# use phusion's init system
CMD ["/sbin/my_init"]