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
        python3-pip \
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

# install Zok's Omni Config Changer
COPY omni-config-changer /usr/local/lib/occ
RUN pip install /usr/local/lib/occ

# Omni Config Changer settings
ENV OC_SCHEME=bashlike \
    OC_FILE=/etc/arkmanager/instance.cfg \
    OC_FOLDER=/etc/arkmanager/

# install startup script
COPY --chmod=777 /scripts/startup.py /etc/my_init.d/12-setup-config.py
COPY --chmod=777 /scripts/update.py /etc/my_init.d/15-update-server.py
COPY --chmod=777 /scripts/run.py /etc/my_init.d/20-run-instance.py

COPY arkmanager-changeset.cfg /etc/arkmanager/

# use phusion's init system
CMD ["/sbin/my_init"]