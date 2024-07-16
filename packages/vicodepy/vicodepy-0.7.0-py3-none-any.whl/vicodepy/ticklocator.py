# ViCodePy - A video coder for psychological experiments
#
# Copyright (C) 2024 Esteban Milleret
# Copyright (C) 2024 Rafael Laboissière
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>.

from math import floor, ceil, log10
from numpy import arange
from PySide6.QtGui import QFontMetrics


class TickLocator:
    def find_locations(self, tmin, tmax, width, font, min_gap):
        """Arguments:\
    tmin: minimum time in the timescale (in seconds)
    tmax: maximum time in the timescale (in seconds)
    width: width of the timeline (in pixels)
    font: QFont to be used
    min_gap: minimum acceptable distance in labels (in percent of widest label)

Value: list of [location, label] lists
"""
        gap_prev = None
        delta_prev = None
        fm = QFontMetrics(font)
        delta = 1
        while True:
            imax = delta * floor(tmax / delta)
            imin = delta * ceil(tmin / delta)
            nb_int_digit = floor(log10(imax)) + 1
            nb_dec_digit = floor(log10(delta))
            if nb_int_digit > 0:
                label = "0" * nb_int_digit
            else:
                label = "0"
            if nb_dec_digit < 0:
                label += "." + "0" * -nb_dec_digit
            text_width = fm.boundingRect(label).width() * (tmax - tmin) / width
            gap = (delta - text_width) / text_width
            if gap >= min_gap:
                if gap_prev and gap_prev < min_gap:
                    break
                else:
                    delta_prev = delta
                    delta = self.change(delta, "decrease")
            else:
                if gap_prev and gap_prev >= min_gap:
                    delta = delta_prev
                    break
                else:
                    delta_prev = delta
                    delta = self.change(delta, "increase")
            gap_prev = gap
        retval = []
        fmt = f"{{:.{max([0, -floor(log10(delta))])}f}}"
        for t in arange(imin, imax + delta, delta):
            label = fmt.format(t)
            label_width = fm.boundingRect(label).width() * (tmax - tmin) / width
            if (t - label_width / 2 > tmin) and (t + label_width / 2 < tmax):
                retval.append([t, label])
        return retval

    def change(self, delta, direction):
        logdelta = log10(delta)
        factor = 10 ** floor(logdelta)
        last = round(10**logdelta / factor)
        if direction == "decrease":
            if last == 1:
                last = 0.5
            else:
                if last == 2:
                    last = 1
                else:
                    last = 2
        else:
            if last == 1:
                last = 2
            else:
                if last == 2:
                    last = 5
                else:
                    last = 10
        return factor * last
