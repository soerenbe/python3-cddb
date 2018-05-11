"""
python3-cddb

Copyright (C) 2018 Sören Berger <soeren.berger (at) u1337.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import requests

from . results import CDDBTitle, CDDBResult

DEFAULT_USER = 'unknown'
DEFAULT_HOSTNAME = 'localhost'
DEFAULT_SERVER = 'http://freedb.freedb.org/~cddb/cddb.cgi'
DEFAULT_CLIENT_NAME = 'python3-cddb'
# To ensure that there is only one result we query with protocol level 1
# Future improvement: Use protocol level 6 for UTF-8 support.
QUERY_PROTOCOL = 1
# Protocol level 6 sends UTF-8 that we can encode.
# See http://ftp.freedb.org/pub/freedb/latest/CDDBPROTO
# for more information about the protocol levels
READ_PROTOCOL = 6
VERSION = 0.1


class CDDBClient:

    def __init__(self, disc, user=None, hostname=None, server=None, client_name=None):
        self.disc = disc
        self.user = user or DEFAULT_USER
        self.hostname = hostname or DEFAULT_HOSTNAME
        self.server = server or DEFAULT_SERVER
        self.client_name = client_name or DEFAULT_CLIENT_NAME

    def _build_query(self, command, extra_command=None, protocol=QUERY_PROTOCOL):
        if command not in ['query', 'read']:
            raise Exception('Invalid CDDB command: %s' % command)
        if protocol not in range(1, 7):
            raise Exception('Invalid CDDB protocol level: %i' % protocol)
        url = self.server
        url += "?cmd=cddb+%s" % command
        if extra_command:
            url += "+" + "+".join([str(i) for i in extra_command])
        url += "&hello=%s+%s+%s+%s" % (self.user, self.hostname, self.client_name, VERSION)
        url += "&proto=%i" % protocol
        return url

    def query(self):
        # For each track we need the offsets
        disc_offsets = [str(i.offset) for i in self.disc.tracks]
        # Finally append to seconds of the complete disc
        disc_offsets.append(self.disc.seconds)
        # This combined give additional parameters for the URL
        extra_query = [self.disc.freedb_id, len(self.disc.tracks)] + disc_offsets
        url = self._build_query('query', extra_query, QUERY_PROTOCOL)
        x = requests.get(url)
        d = x.content.decode('utf-8')
        return_code, _ = d.split(' ', 1)
        if return_code != "200":
            raise Exception("WRONG RETURN: %s" % return_code)
        return_code, category, disc_id, disc_name = d.split(' ', 3)
        return self.query_category(category)

    def query_category(self, category):
        extra_query = [category, self.disc.freedb_id]
        url = self._build_query('read', extra_query, READ_PROTOCOL)
        x = requests.get(url)
        r = x.content.decode('utf-8')
        l = r.split('\n')
        result_dict = {}
        for i in l:
            if i.count('=') == 0:
                continue
            k, v = i.split('=')
            if k in result_dict:
                result_dict[k] += v[:-1]
            else:
                result_dict[k] = v[:-1]
        print(CDDBResult.from_query(result_dict))
        return result_dict
