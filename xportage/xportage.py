#
# Copyright (C) 2006-2015 Wyplay, All Rights Reserved.
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

import os, sys

os.environ["PORTAGE_LEGACY_GLOBALS"] = "false"
import portage
from portage.const import INCREMENTALS
from portage.util import LazyItemsDict
import portage.exception
del os.environ["PORTAGE_LEGACY_GLOBALS"]

from exceptions import Exception

class XPortageError(Exception):
        """ Error class for Xportage. """
        def __init__(self, error):
                self.error = error.strip(" \t\n")

        def get_error(self):
                return self.error

        def __str__(self):
                return self.get_error()

class XPortage(object):
        def __init__(self, root=None, config_root=None):
                self.settings = None
                self.trees = None
                self.portdb = None
                self.config_root = None 
                self.root = None
                self.config = None

                if root:
                        self.parse_config(root, config_root)

        def parse_config(self, root="/", config_root=None, clone=None, store=True):
                root = os.path.realpath(root) + '/'

                if not config_root:
                        config_root = root
                else:
                        config_root = os.path.realpath(config_root) + '/'

                if not os.path.isdir(root):
                        raise XPortageError("Can't find directory %s" % root)

                try:
                        config = portage.config(clone=clone,
                                                mycpv=None,
                                                config_profile_path=None,
                                                config_incrementals=INCREMENTALS,
                                                config_root = config_root,
                                                target_root = root,
                                                local_config=True)
                except Exception, e:
                        raise XPortageError('Portage error: %s' % e)
                if store:
                        self.config = config
                        self.settings = None
                        self.trees = None
                        self.portdb = None
                        self.config_root = config_root
                        self.root = root

                return config

        def create_trees(self, config=None, store=True):
                if not config:
                        if self.config:
                                config = self.config
                        else:
                                raise XPortageError("No config parsed can't create trees")

                if store and self.trees:
                        for myroot in self.trees:
                                portdb = self.trees[myroot]["porttree"].dbapi
                                portdb.close_caches()
                                del self.trees[myroot]["porttree"], myroot, portdb
                                trees = self.trees
                else:
                        trees = {}

                settings = config
                settings.lock()

                myroots = [(settings["ROOT"], settings)]
                if settings["ROOT"] != "/":
                        settings = portage.config(config_root=None, target_root=None,
                                                  config_incrementals=INCREMENTALS)
                        # When ROOT != "/" we only want overrides from the calling
                        # environment to apply to the config that's associated
                        # with ROOT != "/", so we wipe out the "backupenv" for the
                        # config that is associated with ROOT == "/" and regenerate
                        # it's incrementals.
                        # Preserve backupenv values that are initialized in the config
                        # constructor. Also, preserve XARGS since it is set by the
                        # portage.data module.

                        backupenv_whitelist = settings._environ_whitelist
                        backupenv = settings.configdict["backupenv"]
                        env_d = settings.configdict["env.d"]
                        for k, v in os.environ.iteritems():
                                if k in backupenv_whitelist:
                                        continue
                                if k in env_d or \
                                        v == backupenv.get(k):
                                        backupenv.pop(k, None)
                        settings.regenerate()
                        settings.lock()
                        myroots.append((settings["ROOT"], settings))

                for myroot, mysettings in myroots:
                        trees[myroot] = LazyItemsDict(trees.get(myroot, None))
                        trees[myroot].addLazySingleton("virtuals", mysettings.getvirtuals, myroot)
                        trees[myroot].addLazySingleton(
                                        "vartree", portage.vartree, myroot, categories=mysettings.categories,
                                        settings=mysettings)
                        trees[myroot].addLazySingleton("porttree",
                                        portage.portagetree, myroot, settings=mysettings)
                        trees[myroot].addLazySingleton("bintree",
                                        portage.binarytree, myroot, mysettings["PKGDIR"], settings=mysettings)

                settings = trees["/"]["vartree"].settings
                
                for myroot in trees:
                        trees[myroot]["porttree"].dbapi.freeze()
                        if myroot != "/":
                                settings = trees[myroot]["vartree"].settings
                                break
                if store:
                        self.trees = trees
                        self.settings = settings
                        self.portdb = self.trees[self.settings["ROOT"]]["porttree"].dbapi

                return trees

        def best_match(self, pkg_atom):
                if not self.portdb:
                        raise XPortageError("Trees not built can't search for packages.")
                
                try:
                        target = self.portdb.xmatch("bestmatch-visible", pkg_atom)
                except KeyError, e:
                        raise XPortageError("Portage error: %s" % e)

                if not target: # return None when empty string
                        return None
                return target

        def match_all(self, pkg_atom, multi=False):
                if not self.portdb:
                        raise XPortageError("Trees not built can't search for packages.")
   
                try:
                        target = self.portdb.xmatch("match-all", pkg_atom)
                except KeyError, e:
                        raise XPortageError("Portage error: %s" % e)
                except ValueError, e:
                        if multi:
                                target = []
                                for pp in e[0]:
                                        try:
                                                target += self.portdb.xmatch("match-all", pp)
                                        except KeyError, e:
                                                raise XPortageError("Portage error: %s" % e)
                        else:
                                raise XPortageError("The short target ebuild: %s is ambiguous. Please specify one the following fully-qualified target ebuild instead:\n%s" % (pkg_atom, ' '.join(e[0])))
                if not target:
                        return []
                return target

        def doebuild(self, ebuild, arg):
                settings = portage.config(clone=self.settings)
                settings.unlock()
                portage.doebuild(ebuild, arg, portage.root, settings, tree="porttree")

