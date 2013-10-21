#!/bin/sh
nosetests --with-coverage --cover-html --cover-package=interfaces --cover-package=modules --cover-package=store --cover-package=utils
doxygen GISMOH.doxy