# -*- coding: utf-8 -*-
"""
    rhodecode.lib.dbmigrate.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Database migration modules
    
    :created_on: Dec 11, 2010
    :author: marcink
    :copyright: (C) 2009-2010 Marcin Kuzminski <marcin@python-works.com>    
    :license: GPLv3, see COPYING for more details.
"""
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; version 2
# of the License or (at your opinion) any later version of the license.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.

import logging
from sqlalchemy import engine_from_config

from rhodecode import __dbversion__
from rhodecode.lib.dbmigrate.migrate.versioning import api
from rhodecode.lib.dbmigrate.migrate.exceptions import \
    DatabaseNotControlledError
from rhodecode.lib.utils import BasePasterCommand, Command, add_cache

log = logging.getLogger(__name__)

class UpgradeDb(BasePasterCommand):
    """Command used for paster to upgrade our database to newer version
    """

    max_args = 1
    min_args = 1

    usage = "CONFIG_FILE"
    summary = "Upgrades current db to newer version given configuration file"
    group_name = "RhodeCode"

    parser = Command.standard_parser(verbose=True)

    def command(self):
        from pylons import config

        add_cache(config)

        #engine = engine_from_config(config, 'sqlalchemy.db1.')

        repository_path = 'rhodecode/lib/dbmigrate'
        db_uri = config['sqlalchemy.db1.url']

        try:
            curr_version = api.db_version(db_uri, repository_path)
            msg = ('Found current database under version'
                 ' control with version %s' % curr_version)

        except (RuntimeError, DatabaseNotControlledError), e:
            curr_version = 1
            msg = ('Current database is not under version control setting'
                   ' as version %s' % curr_version)
            api.version_control(db_uri, repository_path, curr_version)


        print msg
        #now we have our dbversion we can do upgrade

        msg = 'attempting to do database upgrade to version %s' % __dbversion__
        print msg
        api.upgrade(db_uri, repository_path, __dbversion__)

    def update_parser(self):
        self.parser.add_option('--sql',
                      action='store_true',
                      dest='just_sql',
                      help="Prints upgrade sql for further investigation",
                      default=False)
