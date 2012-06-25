#! /usr/bin/env python2
# *** coding: utf-8 ***
# pylint: disable=I0011
#
# Based on http://assela.pathirana.net/Sozi
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
"""
    Automate adding new frames to a Sozi presentation.
    
    - Add a template frame (rect) with ID "autoframe-anchor" to your document, 
      and a (title) text identified by "autoframe-title"
    - Make sure you have at least one Sozi frame already added to your document
    - Call the script with two arguments, your document file and the name 
      of a file containing titles ('-' for stdin)
    - A new frame will be added for every title, to the OUTSIDE of the page frame, 
      the text will contain the title, so you know what's what
    - Backups will be created automatically
    - Now reload your document in InkScape and move the new frames where you need them

    - Call the script with just a Sozi document to list the contained frames
   
"""
# TODO: make it into an inkscape extension
# TODO: read the titles from the title template node (multi-line) so we need no interface
import os
import re
import sys
import time
from copy import deepcopy
from lxml import etree

NS_SVG  = "{http://www.w3.org/2000/svg}"
NS_INK = "{http://www.inkscape.org/namespaces/inkscape}"
NS_SOZI = "{http://sozi.baierouge.fr}"


def new_id(frame_ids):
    "Create new unique ID"
    for count in range(2*len(frame_ids)):
        frame_id = "frame%d" % (count + 1)
        if frame_id not in frame_ids:
            frame_ids.add(frame_id)
            return frame_id


def clone(target, node):
    "Clone an element"
    copied = deepcopy(node)
    clone.next_id += 1 # BOGUS pylint: disable=E1101, W0612
    copied.attrib["id"] = "autoframe-%d" % clone.next_id # BOGUS pylint: disable=E1101
    target.append(copied)
    return copied

clone.next_id = int(time.time())


def save_tree(filename, tree):
    "Save XML tree to existing file, making a backup."
    stamp = time.time()
    tmpfile = ".autoframe_%s,%d" % (filename, stamp)
    tree.write(tmpfile, pretty_print=True)
    os.rename(filename, "%s,%d" % (filename, stamp))
    os.rename(tmpfile, filename)


def main():
    "Sozi autoframe script"
    if len(sys.argv) < 2:
        print "Usage: $0 <svg file> <\"id\">\n"
        exit(5)

    mainfile, titlefile  =  (sys.argv + [None])[1:3]
    
    # Load presentation and find the frames
    tree = etree.parse(mainfile)
    frames = dict((int(node.attrib[NS_SOZI + "sequence"], 10), node)
        for node in tree.findall("//%sframe" % NS_SOZI)
    )
    frame_ids = set((frame.attrib["id"] for frame in frames.itervalues()))
    ##print frame_ids

    if titlefile is None:
        # Just list the frames
        for idx, frame in sorted(frames.iteritems()):
            print "%3d %-15s %s → %s" % (
                idx, 
                frame.attrib["id"],
                frame.attrib[NS_SOZI + "title"], 
                frame.attrib[NS_SOZI + "refid"],
            )
        return

    # Find template elements
    templ_anchor = tree.xpath("//*[@id='autoframe-anchor']")[0]
    templ_title = tree.xpath("//*[@id='autoframe-title']")[0]

    # Read titles and add new nodes
    root = tree.getroot()
    lastframe = frames[max(frames)]
    seq = max((int(frame.attrib[NS_SOZI + "sequence"]) for frame in frames.itervalues()))
    pos, offset = 0, float(templ_anchor.attrib["height"]) + 10

    for title in (sys.stdin if titlefile == "-" else open(titlefile, "r")):
        title = title.strip()
        seq += 1

        # View anchor referenced by the frame (must have a "height" attribute, e.g. be a rect")
        # TODO: could query the height via calling inkscape and so handle any element
        newanchor = clone(root, templ_anchor)
        newanchor.attrib[NS_INK + "label"] = '#' + re.sub("[^A-Za-z0-9]+", "_", title)
        newanchor.attrib["y"] = str(float(newanchor.attrib["y"]) + pos)

        # Note that we expect a text node with a contained tspan here!
        newtitle = clone(root, templ_title)
        newtitle.attrib["y"] = str(float(newtitle.attrib["y"]) + pos)
        newtitle.getchildren()[0].text = title

        # Add the new frame
        newframe = clone(root, lastframe)
        newframe.attrib["id"] = new_id(frame_ids)
        newframe.attrib[NS_SOZI + "sequence"] = str(seq)
        newframe.attrib[NS_SOZI + "title"] = title
        newframe.attrib[NS_SOZI + "refid"] = newanchor.attrib["id"]

        pos += offset

    # Write result
    save_tree(mainfile, tree)


if __name__  ==  "__main__":
    main()

