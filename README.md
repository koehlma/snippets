About
=====
Some code snippets in various programming languages I wrote and don't became a
project.
Just some experiments or stuff came into my mind and I want to try.
Normally not active development and no documentation here.

HTML
====
[Periodic Table](http://koehlma.github.com/snippets/html/periodictable.html):
A Periodic Table with some special effects based only on HTML and CSS3.

JavaScript
==========
[Chroma-Key](https://github.com/koehlma/snippets/blob/master/javascript/chroma-key.js):
A JavaScript based Chroma-Key for HTML5-canvas.
This actually does it's job, but sometimes it is very slow.
For serious chroma-keying with JavaScript I would recommend [Seriously.js](https://github.com/brianchirls/Seriously.js).

Programs
========
[bootimg.py](https://github.com/koehlma/snippets/blob/master/programs/bootimg.py):
A tool to take Android's `boot.img` apart.
It displays also all meta information of the specified `boot.img`.
Usage: `bootimg.py <image file>`.

[getmem.py](https://github.com/koehlma/snippets/blob/master/programs/getmem.py):
A tool to get a full memory dump for a program running with a specified pid.
It uses the GNU-Debugger and is useful for debugging or reverse engineering.
Usage: `getmem.py <pid> <output directory>`.

[imagetool.sh](https://github.com/koehlma/snippets/blob/master/programs/imagetool.sh):
If you have a hard drive dump for example and you want to access the partitions
on this dump this tool is the tool you are searching for.
It could create and partition images as well as format or mount partitions on
images.
Usage: menu based interface - just start it.

[portscanner.py](https://github.com/koehlma/snippets/blob/master/programs/portscanner.py):
Just wrote this because I was abroad and forgot to install nmap but I wanted to
scan the network.
It uses the Connect-Scan method.
For serious portscanning I would recommend you [nmap](http://nmap.org/).
Usage: `portscanner.py <ip address> <start port> <end port>`.

Python
======
Fractals
--------
Just a rainy day and I wanted to try something new and interesting.
Then I came across a [Mandelbrot script](https://github.com/koehlma/snippets/blob/master/python/fractals/mandelbrot.py)
in obfuscated Python that looks like a Mandelbrot fractal.
I became interested and tried to do something myself.
The result is a [Python script](https://github.com/koehlma/snippets/blob/master/python/fractals/julia.py)
that renders Julia fractals.
Have a look at the [results](https://github.com/koehlma/snippets/tree/master/python/fractals).

GPlayer
-------
This is just a small wrapper around GStreamer's Python bindings which makes them
more intuitive and brings the ability to play out of Python's file objects.

[Source](https://github.com/koehlma/snippets/blob/master/python/gplayer/gplayer.py), 
[Example](https://github.com/koehlma/snippets/blob/master/python/gplayer/example.py), 
[Documentation](http://koehlma.github.com/snippets/gplayer/)

DNS
---
DNS protocol implementation in pure Python.
Please check the [source](https://github.com/koehlma/snippets/blob/master/python/network/dns.py)
for more information.

TUN/TAP
-------
Small wrapper around `/dev/net/tun` to control TUN and TAP devices out of Python.
Please check the [source](https://github.com/koehlma/snippets/blob/master/python/network/tuntap.py)
for more information.







