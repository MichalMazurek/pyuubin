#!/bin/bash

REMOTE_REPOSITORY_WITH_USER=$1

pip3 install -U pip

if [ ! -e ${REMOTE_REPOSITORY_WITH_USER}  ]; then
    pip3 install --extra-index-url ${REMOTE_REPOSITORY_WITH_USER} "yuubin==${YUUBIN_VERSION}"
else
    pip3 install "yuubin==${YUUBIN_VERSION}"
fi