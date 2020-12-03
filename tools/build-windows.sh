#!/bin/bash

VERSION=`python -c 'import version; print(version.version)'`

rm -rf build/* dist/*

source env/Scripts/activate
rm -rf dist/spacehaven-modloader dist/spacehaven-modloader-$VERSION.windows
python -m PyInstaller --noconsole spacehaven-modloader.spec

mv dist/spacehaven-modloader dist/spacehaven-modloader-$VERSION.windows

echo "-- Press enter key to continue --"
read $null
start dist
