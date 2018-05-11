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


class CDDBResult:
    def __init__(self, album_artist, album_title, discid, year, genre, extra_info, playorder):
        self.album_artist = album_artist
        self.album_title = album_title
        self.discid = discid
        self.year = year
        self.genre = genre
        self.playorder = playorder
        self.tracks = []
        self.extra_info = extra_info

    def __str__(self):
        return '<%s : [%s tracks of %s from %s] %s - %s>' % (self.__class__.__name__,
                                                           len(self.tracks),
                                                           self.genre,
                                                           self.year,
                                                           self.album_artist,
                                                           self.album_title)

    @property
    def track_count(self):
        return len(self.tracks)

    @classmethod
    def from_query(cls, result_dict):
        album_artist, album_title = result_dict['DTITLE'].split(' / ')
        result = cls(album_artist,
                     album_title,
                     result_dict['DISCID'],
                     result_dict['DYEAR'],
                     result_dict['DGENRE'],
                     result_dict['EXTD'],
                     result_dict['PLAYORDER']
                     )
        counter = 0
        while "TTITLE%s" % counter in result_dict:
            track_detail = result_dict['TTITLE%s' % counter]
            if ' / ' in track_detail:
                track_artist, track_title = track_detail.split(' / ')
            else:
                track_artist = album_artist
                track_title = track_detail
            t = CDDBTitle(counter+1, track_artist, track_title, result_dict['EXTT%s' % counter])
            result.tracks.append(t)
            counter += 1

        return result


class CDDBTitle:
    def __init__(self, track_no, artist, title, extt):
        self.track_no = track_no
        self.artist = artist
        self.title = title
        self.extt = extt

    def __str__(self):
        return "<%s: #%s %s - %s>" % (self.__class__.__name__, self.track_no, self.artist, self.title)