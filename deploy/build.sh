#!/usr/bin/env bash

NAME="deploy"
VERSION="1.0.0"
HASH_CMD="md5 sha1 sha256"
PREFIX=$NAME-$VERSION-win_x64
ICO_PATH="ico/$NAME-$VERSION-48x48.ico"


rm -rf build/ rm -rf dist/

if [ -f $NAME.spec ]; then
  pyinstaller --clean $NAME.spec
  mkdir -p release
  cp dist/$NAME.exe dist/$PREFIX.exe
  cp dist/$PREFIX.exe release/
  for hash in $HASH_CMD; do
    ${hash}sum dist/$PREFIX.exe | awk '{print $1}' > dist/$PREFIX.${hash}
    cp -rf dist/$PREFIX.${hash} release/
  done
else
  pyi-makespec --icon $ICO_PATH -F $NAME/$NAME.py
fi
