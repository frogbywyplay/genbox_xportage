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
import xportage

CONFIG1="%s/config1" % curr_path
CONFIG2="%s/config2" % curr_path

class xportageTester(unittest.TestCase):

        def __init__(self, methodName='runTest'):
                unittest.TestCase.__init__(self, methodName)
                self.path = os.path.realpath(os.path.dirname(sys.modules[__name__].__file__))
        
        def testWrongConfig(self):
                try:
                        p = xportage.XPortage("./bleuargs")
                except xportage.XPortageError:
                        return
                self.fail('an error should have been raised')

        def testConfig(self):
		if not os.path.exists(CONFIG1):
			self.fail('%s is missing: skipping test' % CONFIG1)
			return
                p = xportage.XPortage()
                p.parse_config(CONFIG1)
                self.failUnlessEqual(p.config["ARCH"], 'sh')
                self.failUnlessEqual(os.path.normpath(p.config["PORTDIR"]), os.path.normpath("%s/portage/targets" % p.root))
                del p

        def testTrees(self):
		if not os.path.exists(CONFIG1):
			self.fail('%s is missing: skipping test' % CONFIG1)
			return
                p = xportage.XPortage(CONFIG1)
                p.create_trees()
                self.failUnless(p.portdb != None)
                self.failUnless(p.trees != None)
                self.failUnless(p.settings != None)
                self.failUnless(p.trees[p.root] != None)
                self.failUnless(p.trees['/'] != None)
                try:
                        p.create_trees()
                except:
                        self.fail("Can't reload trees")
                del p

        def testPortdb(self):
		if not os.path.exists(CONFIG1):
			self.fail('%s is missing: skipping test' % CONFIG1)
			return
                p = xportage.XPortage(CONFIG1)
                p.create_trees()
                self.failUnlessEqual(p.portdb.findname("base-targets/wms-1.3.15.0"),
                                     '%sportage/targets/base-targets/wms/wms-1.3.15.0.ebuild' % p.root)
                self.failUnless('base-targets/wms' in p.portdb.cp_all())
                del p

        def testBestMatch(self):
		if not os.path.exists(CONFIG1):
			self.fail('%s is missing: skipping test' % CONFIG1)
			return
                os.environ['ACCEPT_KEYWORDS'] = 'mdboxa'
                p = xportage.XPortage(CONFIG1)
                p.create_trees()
                self.failUnlessEqual(p.best_match("X1"), 'base-targets/X1-1.4.0.42')
                self.failUnlessEqual(p.best_match('busybox'), None)
                os.environ['ACCEPT_KEYWORDS'] = ''
                p.parse_config(p.root)
                p.create_trees()
                self.failUnlessEqual(p.best_match("X1"), None)

        def testMatchAll(self):
		if not os.path.exists(CONFIG1):
			self.fail('%s is missing: skipping test' % CONFIG1)
			return
                p = xportage.XPortage(CONFIG1)
                p.create_trees()
                self.failUnlessEqual(p.match_all("X1"), ['base-targets/X1-1.4.0.0', 'base-targets/X1-1.4.0.42'])
                self.failUnlessEqual(p.match_all('busybox'), [])
                self.failUnlessEqual(p.match_all('<base-targets/X1-1.4.0.12'), ['base-targets/X1-1.4.0.0'])
                self.failUnlessEqual(p.match_all('>=base-targets/X1-1.4.0.12'), ['base-targets/X1-1.4.0.42'])

        def testStore(self):
		if not os.path.exists(CONFIG1):
			self.fail('%s is missing: skipping test' % CONFIG1)
			return
                p = xportage.XPortage(CONFIG1)
                p.create_trees()
                new_config = p.parse_config(root=CONFIG2, store=False)
                self.failUnlessEqual(new_config['ARCH'], 'x86')
                self.failUnlessEqual(p.settings['ARCH'], 'sh')
                new_trees = p.create_trees(config=new_config, store=False)
                self.failUnlessEqual(p.settings['ARCH'], 'sh')
                self.failUnless(p.trees[p.root] != None)
                self.failUnlessEqual(p.trees[p.root]['porttree'].dbapi.porttrees,
                                     [p.root + 'portage/targets', p.root + 'portage/x1'])
                self.failUnlessEqual(new_trees[new_config['ROOT']]['porttree'].dbapi.porttrees,
                                     [new_config['ROOT'] + 'portage/x86'])
                self.failUnlessEqual(p.match_all("X1"), ['base-targets/X1-1.4.0.0', 'base-targets/X1-1.4.0.42'])

if __name__ == "__main__":
        unittest.main()

