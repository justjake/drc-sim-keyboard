#!/usr/bin/env bash
# Installs dependencies of drc-sim.py
set -e

sudo apt-get install \
  build-essential \
  python-dev \
  libffi-dev \
  libavcodec-dev \
  libswscale-dev \
  libsdl-dev \
  libsmpeg-dev \
  python-pygame

sudo pip install \
  cffi \
  constructor \

echo these bits arent idempotent
echo run them yourself:
echo   wget https://people.csail.mit.edu/hubert/pyaudio/packages/python-pyaudio_0.2.8-1_amd64.deb
echo   sudo dpkg -i ./python-pyaudio*.deb
