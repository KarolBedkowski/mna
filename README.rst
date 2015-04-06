+++++++++++++++++
 MNA ver 0.x.x
+++++++++++++++++

:Credits: Copyright (c) Karol Będkowski, 2014-2015
:Licence: GPLv2+
:Status: alpha (working, bugs)
:Tags: news agent, news aggregator, rss, website monitoring


News aggregate & websites changes monitoring application.


Disclaimer
==========

This is experimental software. THERE IS NO WARRANTY FOR THIS PROGRAM.

Author shall not be responsible for loss of data under any circumstance.


Installation
============

1. unpack
2. run: make
3. launch via: ./mna.py


Runtime Requirements
--------------------
* Python 2.7.x
* sqlalchemy 0.7.9+
* pyqt4 (with webkit)


Files
-----

~/.config/mna/mna.cfg
   application configuration 

~/.local/share/mna/mna.db
   sources configuration & articles storage 

~/.cache/mna
   cache for source specific files (i.e. favicons)


Licence
=======

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

For details please see COPYING file.

Credits
=======


.. vim: ft=rst tw=72
