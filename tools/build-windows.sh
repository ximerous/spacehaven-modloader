#!/bin/bash

OLDPATH=$PATH
source env/Scripts/activate
VERSION=`python -c 'import version; print(version.version)'`

deactivate
rm -rf build/* dist/spacehaven-modloader dist/spacehaven-modloader-$VERSION.windows
source env/Scripts/activate

python -m PyInstaller --noconsole modloader.spec
deactivate

PATH=$OLDPATH
mv dist/spacehaven-modloader dist/spacehaven-modloader-$VERSION.windows

echo "-- Press enter key to continue --"
read $null
start dist
