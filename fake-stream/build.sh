#!/usr/bin/env bash

MAIN="MainGUI"
NAME="FakeStream"
VERSION="2.0.0"
HASH_CMD="md5 sha1 sha256"
PREFIX=$NAME-$VERSION-win_x64
ICO_PATH="ico/$NAME-$VERSION-48x48.ico"


rm -rf build/ rm -rf dist/

pyinstaller --clean -F $NAME/$MAIN.py -i $ICO_PATH -w
mkdir -p release
cp dist/$MAIN.exe dist/$PREFIX.exe
cp dist/$PREFIX.exe release/
for hash in $HASH_CMD; do
  ${hash}sum dist/$PREFIX.exe | awk '{print $1}' > dist/$PREFIX.${hash}
  cp -rf dist/$PREFIX.${hash} release/
done
