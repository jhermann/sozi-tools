# sozi-tools

## Helpers for Inkscape / Sozi presentations

**portasvg.sh** makes editable SVG files portable (no external images or fonts needed) and as small as possible.
For all SVG files in the current directory, it creates a portable copy in the `portable` subdirectory, by 
converting all texts to paths, embedding any external images, and vacuuming redundant definitions to reduce file size.
The resulting files have no more references to resources in the local filesystem or only locally available fonts, 
and also render faster in common browsers (especially important for Sozi documents).
To use it, you need to have *Inkscape* and *xvfb* installed.

**autoframe.py** simplifies the work needed to add a lot of Sozi frames to a document, so that you need to call the 
Sozi extension just once, to put the new frames added into the desired order and set any special attributes, instead 
of doing that for each single frame. See the module docstring in the script for more details on how to prepare your
document and calling it. 
You also need to have lxml available (`aptitude install python-lxml`, or `aptitude install libxml2-dev libxslt-dev` 
followed by `pip install lxml`).

The included `autoframe.svg` example contains two inner frames that were created using 

```sh
$ ./autoframe.py autoframe.svg autoframe-titles.txt
```

and then moved and re-ordered, you can see that the initial `frame1` was moved behind the newly created ones:

```sh
$ ./autoframe.py autoframe.svg
  1 frame2          Automate → autoframe-1340627041
  2 frame3          Be happy! → autoframe-1340627044
  3 frame1          Life, the Universe and Everything → rect2985-2
```

## Links
 * http://inkscape.org/
 * http://sozi.baierouge.fr/wiki/en:welcome
