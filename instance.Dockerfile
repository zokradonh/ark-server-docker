# syntax=docker/dockerfile:1.4

FROM ubuntu:jammy

LABEL \
    org.opencontainers.image.authors="zokradonh <az@zok.xyz>" \
    org.opencontainers.image.title="ARK Survival Evolved Dedicated Server" \
    org.opencontainers.image.description="One container for one ARK instance" \
    org.opencontainers.image.url="https://github.com/zokradonh/ark-server-docker" \
    org.opencontainers.image.source="https://github.com/zokradonh/ark-server-docker"

RUN <<EOT
    # install required ubuntu packages
    echo steam steam/question select "I AGREE" | debconf-set-selections
    echo steam steam/license note '' | debconf-set-selections
    add-apt-repository multiverse
    dpkg --add-architecture i386
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        perl \
        rsync \
        curl \
        lsof \
        libc6-i386 \
        lib32gcc-s1 \
        bzip2 \
        tini \
        python3 \
        python3-pip \
        steamcmd
    rm -rf /var/lib/apt/lists/*
    ln -sf /usr/games/steamcmd /usr/bin/steamcmd
EOT

# creating /home/steam/.steam to avoid two error messages on steamcmd start
ENV UID=1000 \
    GID=1000
RUN <<EOT 
    # configure steamcmd
    addgroup --gid $GID steam
    adduser --system --uid $UID --gid $GID --shell /bin/bash steam
    mkdir -p /home/steam/.steam
    runuser -u steam steamcmd +quit
EOT

RUN <<EOT
    # install arkmanager
    curl -sL https://git.io/arkmanager | bash -s steam
EOT

# install Zok's Omni Config Changer
COPY omni-config-changer /usr/local/lib/occ
RUN pip install /usr/local/lib/occ

# Omni Config Changer settings
ENV OC_SCHEME=bashlike \
    OC_FILE=/etc/arkmanager/instance.cfg \
    OC_FOLDER=/etc/arkmanager/
COPY arkmanager-changeset.cfg /etc/arkmanager/

# install startup script
COPY --chmod=777 /scripts/startup.py /startup.py

STOPSIGNAL SIGINT

ENTRYPOINT ["/usr/bin/tini","-g","--"]

CMD ["/startup.py"]