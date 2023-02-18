#!/usr/bin/env bash

NAME="deploy"
VERSION="2.0.0"
HASH_CMD="md5 sha1 sha256"
PREFIX=$NAME-$VERSION-win_x64
SUFFIX=".exe"
ICO_PATH="ico/$NAME-$VERSION-48x48.ico"

rm -rf build/ rm -rf dist/

os_version=$(uname -a | awk '{print $1}')
if [ $os_version = "Linux" ]; then
  SUFFIX=""
  PREFIX=$NAME-$VERSION-$os_version
fi

if [ -f $NAME.spec ]; then
  pyinstaller --clean $NAME.spec
  mkdir -p release
  cp dist/$NAME${SUFFIX} dist/$PREFIX${SUFFIX}
  cp dist/$PREFIX${SUFFIX} release/
  for hash in $HASH_CMD; do
    ${hash}sum dist/$PREFIX${SUFFIX} | awk '{print $1}' >dist/$PREFIX.${hash}
    cp -rf dist/$PREFIX.${hash} release/
  done
else
  pyi-makespec --icon $ICO_PATH -F $NAME/$NAME.py
fi
