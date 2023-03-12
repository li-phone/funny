#!/usr/bin/env bash

MAIN="MainApp"
NAME="FakeStream"
VERSION="2.1.0"
HASH_CMD="md5 sha1 sha256 sha512"
PREFIX=$NAME-$VERSION-win_x64
SUFFIX=".exe"
ICO_PATH="ico/$NAME-$VERSION-48x48.ico"

rm -rf build/ rm -rf dist/

os_version=$(uname -a | awk '{print $1}')
if [ $os_version = "Linux" ]; then
  SUFFIX=""
  PREFIX=$NAME-$VERSION-$os_version
fi

pyinstaller --clean -F $NAME/$MAIN.py -i $ICO_PATH -w
mkdir -p release
cp dist/$MAIN${SUFFIX} dist/$PREFIX${SUFFIX}
cp dist/$PREFIX${SUFFIX} release/
for hash in $HASH_CMD; do
  ${hash}sum dist/$PREFIX${SUFFIX} | awk '{print $1}' >dist/$PREFIX.${hash}
  cp -rf dist/$PREFIX.${hash} release/
done
