#!/usr/bin/env python3
"""
NOT1MM Logger
Purpose: test alternative sound playing interface
"""
# pylint: disable=unused-import, c-extension-no-member, no-member, invalid-name, too-many-lines, no-name-in-module
# pylint: disable=logging-fstring-interpolation, logging-not-lazy, line-too-long, bare-except

from not1mm.lib.playsound import playsound

import not1mm.fsutils as fsutils

filename = fsutils.APP_DATA_PATH / "phonetics/cq.wav"

playsound(filename, True)
