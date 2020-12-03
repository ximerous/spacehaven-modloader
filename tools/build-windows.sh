#!/bin/bash

OLDPATH=$PATH
source env/Scripts/activate
VERSION=`python -c 'import version; print(version.version)'`

PATH=$OLDPATH
rm -rf build/* dist/spacehaven-modloader dist/spacehaven-modloader-$VERSION.windows

python -m PyInstaller --noconsole spacehaven-modloader.spec
deactivate

PATH=$OLDPATH
mv dist/spacehaven-modloader dist/spacehaven-modloader-$VERSION.windows

echo "-- Press enter key to continue --"
read $null
start dist
