#! /bin/bash
#
# Make editable SVG files portable (no external images or fonts needed)
# and as small as possible
#
# Copyright 2012 Jürgen Hermann
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
use_xvfb=true
inkscape=/usr/bin/inkscape

if $use_xvfb; then
    which xvfb-run >/dev/null || { echo 'Please execute "sudo aptitude install xvfb"!'; exit 1; }
fi
log=$(basename "$0")".log"
test -d portable || mkdir -p portable

case "_$1" in
    _-h | _--help)
        echo "usage: $0"
        echo "Converts all SVG files in the current directory to a portable copy."
        exit 1
        ;;

    _)
        set -e
        : >"$log"
        rm portable/*.svg 2>/dev/null || :
        if $use_xvfb; then
            xvfb-run -a -n 42 -e "$log" "$0" *.svg
        else
            "$0" *.svg
        fi
        exit 0
        ;;
    
    _*)
        set -e
        for name in "$@" ; do 
            portable="portable/$name"
            echo "$name" "»" "$portable"
            echo "$name" "»" "$portable" >>"$log"
            #sed -r -e "s#(file://)?$PWD/(\\./)?##" <"$name" >"$portable"
            cp -p "$name" "$portable"
            $inkscape -g -f "$portable" \
                --verb=EditSelectAllInAllLayers  --verb=ZoomSelection \
                --verb=ObjectToPath --verb=org.ekips.filter.embedimage.noprefs \
                --verb=FileVacuum --verb=FileSave --verb=FileQuit >>"$log"
            sed -i -r -e "s#(file://)?$PWD/(\\./)?(portable/)?##" "$portable"
        done
        exit $?
        ;;
esac

