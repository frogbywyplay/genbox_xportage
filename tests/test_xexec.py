#!/usr/bin/python
#
# Copyright (C) 2006-2014 Wyplay, All Rights Reserved.
# This file is part of xportage.
# 
# xportage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
# 
# xportage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; see file COPYING.
# If not, see <http://www.gnu.org/licenses/>.
#
#


import unittest
import sys, os

curr_path = os.path.realpath(os.path.dirname(sys.modules[__name__].__file__))

sys.path.insert(0, curr_path + '/..')
from xtarget.consts import TARGET_VAR
from subprocess import Popen

import xportage.xexec as xexec

CONFIG1="%s/config1" % curr_path
CONFIG2="%s/config2" % curr_path

def fakeexec(cmd, *args):
        os.stat(cmd)

class xportageTester(unittest.TestCase):

        def __init__(self, methodName='runTest'):
                unittest.TestCase.__init__(self, methodName)
                self.path = os.path.realpath(os.path.dirname(sys.modules[__name__].__file__))
        
        def testXexec1(self):
                oldexec = os.execvpe
                os.execvpe = fakeexec
                os.environ[TARGET_VAR] = self.path
                xexec('/bin/true')
                os.execvpe = oldexec

        def testXexec2(self):
                # no such file
                try:
                        oldexec = os.execvpe
                        os.execvpe = fakeexec
                        os.environ[TARGET_VAR] = self.path
                        xexec('/bin/doesnotexist')
                        os.execvpe = oldexec
                except SystemExit, s:
                        return
                self.fail('binary does not exist, exit should have been called')

        def testXexec3(self):
                # no target
                try:
                        oldexec = os.execvpe
                        os.execvpe = fakeexec
                        os.environ[TARGET_VAR] = self.path + '/doesnotexist'
                        get_current_target = None
                        xexec('/bin/true')
                        os.execvpe = oldexec
                except SystemExit, s:
                        return
                self.fail('target does not exist, exit should have been called')

        def testXexec4(self):
                # empty cmd
                res = 0
                try:
                        oldexec = os.execvpe
                        os.execvpe = fakeexec
                        os.environ[TARGET_VAR] = self.path
                        xexec(None)

                except SystemExit, s:
                        res = 1
                if res == 0:
                        self.fail('cmd is empty, exit should have been called')
                res = 0
                try:
                        oldexec = os.execvpe
                        os.execvpe = fakeexec
                        os.environ[TARGET_VAR] = self.path
                        xexec('')
                        os.execvpe = oldexec
                except SystemExit, s:
                        res = 1
                if res == 0:
                        self.fail('cmd is empty, exit should have been called')

        def testXexec4(self):
                # empty cmd
                try:
                        oldexec = os.execvpe
                        os.execvpe = fakeexec
                        os.environ[TARGET_VAR] = self.path
                        xexec(None)
                        os.execvpe = oldexec
                except SystemExit, s:
                        return
                self.fail('cmd is empty, exit should have been called')

if __name__ == "__main__":
        unittest.main()

