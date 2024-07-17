#!/usr/bin/env python3
####################################################################
#   Copyright (C) 2020-2024 Luis Falcon <falcon@gnuhealth.org>
#   Copyright (C) 2020-2024 GNU Solidario <health@gnusolidario.org>
#   License: GPL v3+
#   Please read the COPYRIGHT and LICENSE files of the package
####################################################################

from mygnuhealth.__init__ import __version__ as myghver
import os

__version__ = myghver

__appname__ = "MyGNUHealth"

__description__ = "The GNU Health Personal Health Record"

__homepage__ = "https://www.gnuhealth.org"

__author__ = "Luis Falcon"

__email__ = "info@gnuhealth.org"

__download_url__ = 'https://ftp.gnu.org/gnu/health/mygnuhealth'

__license__ = "GPL v3+"
__copyright__ = "Copyright 2008-2024 GNU Solidario"

__thanks__ = open(
    os.path.join(os.path.dirname(__file__), "contributors.txt")).read()
