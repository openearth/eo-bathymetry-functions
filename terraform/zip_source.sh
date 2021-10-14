#!/bin/bash
newDir="$1"
targetFile="$2"

newDirPath="../$newDir"

if ! [[ -d "$newDirPath" ]] ; then
    mkdir -p "$newDirPath"
fi
curDir=$(pwd)
cd ..
zip "$newDir/$targetFile" $(find -type f -name "*.py" -o -name "*.txt" | tr '\n' ' ' | sed 's/\.\///g')
cd "$curDir"
