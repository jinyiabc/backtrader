#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2015-2020 Daniel Rodriguez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime
import itertools

from .. import feed, TimeFrame
from ..utils import date2num
from ..utils.py3 import integer_types, string_types
from .csvgeneric import *

class WindCSVData(GenericCSVData):
    params = (('dtformat', '%Y-%m-%d'),)

    def _loadline(self, linetokens):
        # Datetime needs special treatment
        dtfield = linetokens[self.p.datetime]
        if self._dtstr:
            dtformat = self.p.dtformat

            if self.p.time >= 0:
                # add time value and format if it's in a separate field
                dtfield += 'T' + linetokens[self.p.time]
                dtformat += 'T' + self.p.tmformat

            dt = datetime.strptime(dtfield, dtformat)
        else:
            dt = self._dtconvert(dtfield)

        if self.p.timeframe >= TimeFrame.Days:
            # check if the expected end of session is larger than parsed
            if self._tzinput:
                dtin = self._tzinput.localize(dt)  # pytz compatible-ized
            else:
                dtin = dt

            dtnum = date2num(dtin)  # utc'ize

            dteos = datetime.combine(dt.date(), self.p.sessionend)
            dteosnum = self.date2num(dteos)  # utc'ize

            if dteosnum > dtnum:
                self.lines.datetime[0] = dteosnum
            else:
                # Avoid reconversion if already converted dtin == dt
                self.l.datetime[0] = date2num(dt) if self._tzinput else dtnum
        else:
            self.lines.datetime[0] = date2num(dt)

        # The rest of the fields can be done with the same procedure
        for linefield in (x for x in self.getlinealiases() if x != 'datetime'):
            # Get the index created from the passed params
            csvidx = getattr(self.params, linefield)

            if csvidx is None or csvidx < 0:
                # the field will not be present, assignt the "nullvalue"
                csvfield = self.p.nullvalue
            else:
                # get it from the token
                csvfield = linetokens[csvidx]

            if csvfield == '':
                # if empty ... assign the "nullvalue"
                csvfield = self.p.nullvalue

            if csvfield == '--':
                # if empty ... assign the "nullvalue"
                csvfield = 0

            # get the corresponding line reference and set the value
            line = getattr(self.lines, linefield)
            line[0] = float(float(csvfield))

        return True