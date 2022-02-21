# coding=utf-8
"""Utilities / Functions related to Grcard USIM cards

(C) 2021 by Harald Welte <laforge@osmocom.org>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from pytlv.TLV import *
from struct import pack, unpack
from pySim.utils import *
from pySim.filesystem import *
from pySim.ts_102_221 import CardProfileUICC
from pySim.ts_51_011 import EF_IMSI
from pySim.construct import *
from construct import *
import pySim

class EF_OPC(TransparentEF):
    def __init__(self, fid='ff01', sfid=None, name='EF.OPC', desc='A 128-bit value that is derived from OP and K', size={16, 16}):
        super().__init__(fid, sfid=sfid, name=name, desc=desc, size=size)

    def _decode_hex(self, raw_hex):
        return {'OPc': raw_hex}

    def _encode_hex(self, abstract):
        return abstract['OPc']

class EF_K(TransparentEF):
    def __init__(self, fid='ff02', sfid=None, name='EF.K', desc='The Subscriber Key', size={16, 16}):
        super().__init__(fid, sfid=sfid, name=name, desc=desc, size=size)

    def _decode_hex(self, raw_hex):
        return {'K': raw_hex}

    def _encode_hex(self, abstract):
        return abstract['K']

class EF_R1R5(TransparentEF):
    def __init__(self, fid='ff03', sfid=None, name='EF.R1R5', desc='The Rotating Parameter for Key Generation', size={5, 5}):
        super().__init__(fid, sfid=sfid, name=name, desc=desc, size=size)

    def _decode_hex(self, raw_hex):
        return {
            'R1': raw_hex[0:2],
            'R2': raw_hex[2:4],
            'R3': raw_hex[4:6],
            'R4': raw_hex[6:8],
            'R5': raw_hex[8:10]
        }

    def _encode_hex(self, abs):
        return abs['R1']+abs['R2']+abs['R3']+abs['R4']+abs['R5']

class DF_USIM(CardDF):
    def __init__(self):
        super().__init__(fid='7ff0', name='DF.USIM', desc='USIM Configuration')
        files = [
            EF_IMSI(),
            EF_OPC(),
            EF_K(),
            EF_R1R5(),
        ]
        self.add_files(files)

    def decode_select_response(self, resp_hex):
        return pySim.ts_102_221.CardProfileUICC.decode_select_response(resp_hex)

class GrcardUSIM(CardModel):
    _atrs = ["3B 9F 95 80 1F C3 80 31 E0 73 FE 21 13 57 86 81 02 86 98 44 18 A8"]

    @classmethod
    def add_files(cls, rs: RuntimeState):
        """Add Grcard-USIM specific files to given RuntimeState."""
        rs.mf.add_file(TransparentEF('a000', None, 'EF.VERSION', 'The Version of Card'))
        rs.mf.add_file(DF_USIM())
        if 'a0000000871002' in rs.mf.applications:
            usim_adf = rs.mf.applications['a0000000871002']
            files_adf_usim = [
                EF_OPC(),
                EF_K(),
                EF_R1R5(),
            ]
            usim_adf.add_files(files_adf_usim)