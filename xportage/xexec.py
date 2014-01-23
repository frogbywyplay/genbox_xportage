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

import os, sys

from xtarget.config import load_config
from xtarget.current import get_current_target

def xexec(cmd, env=None):
        if env is None:
                env = os.environ.copy()
        current_target = get_current_target()
        if current_target is None:
                print >>sys.stderr, "xexec failed: Can't find current target"
                sys.exit(-1)
        env['PORTAGE_CONFIGROOT'] = current_target + "/root/"
        env['ROOT'] = current_target + "/root/"

        if type(cmd) == str:
                cmd = [cmd]
        if not cmd:
                print >>sys.stderr, "xexec failed: empty cmd"
                sys.exit(-1)
        
        # BEGIN OF SPECIAL HANDLING FOR QFILE
        # TODO: refactor to add a kind of 'rules' per application
        if os.path.basename(cmd[0]) == 'qfile':
                cfg = load_config()
                need_r = False
                for ii in cmd[1:]:
                        if ii.startswith(cfg['targets_dir']):
                                need_r = True
                                break
                if need_r and not '-R' in cmd[1:]:
                        cmd.append('-R')
        # END OF SPECIAL HANDLING FOR QFILE
        try:
                os.execvpe(cmd[0], cmd, env)
        except OSError, e:
                print >>sys.stderr, "xexec failed: %s" % str(e)
                sys.exit(-1)

