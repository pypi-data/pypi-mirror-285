# episoder, https://code.ott.net/episoder
# -*- coding: utf8 -*-
#
# Copyright (C) 2004-2024 Stefan Ott. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json


class RawWrapper():

    def __init__(self, text):

        self._text = text

    def read(self):

        return self._text


class MockResponse():

    def __init__(self, data, encoding, status=200):

        self.raw = RawWrapper(data)
        self.encoding = encoding
        self.status_code = status

    def _get_text(self):

        text = self.raw.read()
        return text.decode(self.encoding, "replace")

    def json(self):

        return json.loads(self.text)

    text = property(_get_text)


class LoggedRequest():

    def __init__(self, method, url, body, headers):

        self.method = method
        self.url = url
        self.body = body
        self.headers = headers
