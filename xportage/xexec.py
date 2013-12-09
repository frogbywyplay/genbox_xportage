#
# Copyright (C) 2006-2013 Wyplay, All Rights Reserved.
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

