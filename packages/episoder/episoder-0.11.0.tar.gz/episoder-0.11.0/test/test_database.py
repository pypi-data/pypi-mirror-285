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

import logging

from os import unlink
from datetime import date, timedelta
from tempfile import mktemp
from unittest import TestCase

from episoder.episoder import Database
from episoder.database import Show, Episode


class TestDatabase(TestCase):

    def setUp(self):

        logging.basicConfig(level=logging.ERROR)
        logging.disable(logging.ERROR)
        self.db = Database("sqlite://")
        self.tempfiles = []

    def tearDown(self):

        for f in self.tempfiles:
            unlink(f)

    def test_str_and_repr(self):

        name = str(self.db)
        self.assertEqual(name, "Episoder Database at sqlite://")

        name = repr(self.db)
        self.assertEqual(name, "Database(sqlite://)")

    def test_get_show_by_url(self):

        show1 = self.db.add_show(Show("test show", url="a"))
        show2 = self.db.add_show(Show("test show 2", url="b"))

        self.assertEqual(show1, self.db.get_show_by_url("a"))
        self.assertEqual(show2, self.db.get_show_by_url("b"))
        self.assertEqual(None, self.db.get_show_by_url("c"))

    def test_get_show_by_id(self):

        show1 = self.db.add_show(Show("test show", url="a"))
        show2 = self.db.add_show(Show("test show 2", url="b"))

        self.assertEqual(show1, self.db.get_show_by_id(show1.id))
        self.assertEqual(show2, self.db.get_show_by_id(show2.id))
        self.assertEqual(None, self.db.get_show_by_id(99999))

    def test_add_show(self):

        show = self.db.add_show(Show("test show", url="http://test2"))
        self.assertTrue(show.id > 0)

        shows = self.db.get_shows()
        self.assertEqual(1, len(shows))
        self.assertIn(show, shows)
        self.db.commit()

        show2 = self.db.add_show(Show("moo show", url="http://test"))
        self.assertTrue(show2.id > 0)
        self.assertNotEqual(show.id, show2.id)
        self.db.commit()

        shows = self.db.get_shows()
        self.assertEqual(2, len(shows))
        self.assertIn(show, shows)
        self.assertIn(show2, shows)

        self.db.add_show(Show("showA", url="urlA"))
        self.assertEqual(3, len(self.db.get_shows()))
        self.db.commit()

        self.db.add_show(Show("showA", url="urlB"))
        self.assertEqual(4, len(self.db.get_shows()))
        self.db.commit()

        with self.assertRaises(Exception):
            self.db.add_show(Show("showB", url="urlB"))
            self.db.commit()

        self.db.rollback()
        self.assertEqual(4, len(self.db.get_shows()))

    def test_add_episode(self):

        show = Show("some show", url="foo")
        show = self.db.add_show(show)
        self.db.commit()

        ep1 = Episode("Some episode", 3, 10, date.today(), "FOO", 30)
        ep2 = Episode("No episode", 3, 12, date.today(), "FOO", 32)
        self.db.add_episode(ep1, show)
        self.db.add_episode(ep2, show)
        self.db.commit()

        episodes = self.db.get_episodes()
        self.assertTrue(ep1 in episodes)
        self.assertTrue(ep2 in episodes)

    def test_search(self):

        show = self.db.add_show(Show("some show"))
        ep1 = Episode("first episode", 3, 10, date.today(), "FOO", 30)
        ep2 = Episode("Second episode", 3, 12, date.today(), "FOO", 32)

        self.db.add_episode(ep1, show)
        self.db.add_episode(ep2, show)
        self.db.commit()

        episodes = self.db.search("first")
        self.assertIn(ep1, episodes)
        self.assertNotIn(ep2, episodes)

        episodes = self.db.search("second")
        self.assertNotIn(ep1, episodes)
        self.assertIn(ep2, episodes)

        episodes = self.db.search("episode")
        self.assertIn(ep1, episodes)
        self.assertIn(ep2, episodes)

        episodes = self.db.search("some show")
        self.assertIn(ep1, episodes)
        self.assertIn(ep2, episodes)

    def test_remove_invalid_show(self):

        self.db.remove_show(0)

    def test_remove_show(self):

        show1 = self.db.add_show(Show("random show", url="z"))
        show2 = self.db.add_show(Show("other show", url="x"))
        self.db.commit()

        now = date.today()
        episode1 = Episode("first", 1, 1, now, "x", 1)
        episode2 = Episode("second", 1, 2, now, "x", 1)
        episode3 = Episode("first", 1, 1, now, "x", 1)

        self.db.add_episode(episode1, show1)
        self.db.add_episode(episode2, show1)
        self.db.add_episode(episode3, show2)
        self.db.commit()

        episodes = self.db.get_episodes()
        self.assertEqual(3, len(episodes))

        self.db.remove_show(show1.id)
        self.db.commit()

        episodes = self.db.get_episodes()
        self.assertEqual(1, len(episodes))
        self.assertIn(episode3, episodes)

    def test_rollback(self):

        show = Show("some show")
        show = self.db.add_show(show)
        self.db.commit()

        ep1 = Episode("first", 3, 10, date.today(), "FOO", 30)
        self.db.add_episode(ep1, show)
        self.db.rollback()

        ep2 = Episode("Second", 3, 12, date.today(), "FOO", 32)
        self.db.add_episode(ep2, show)
        self.db.commit()

        episodes = self.db.get_episodes()
        self.assertFalse(ep1 in episodes)
        self.assertTrue(ep2 in episodes)

    def test_get_episodes(self):

        show = self.db.add_show(Show("some show"))

        today = date.today()
        yesterday = today - timedelta(1)
        before = yesterday - timedelta(1)
        tomorrow = today + timedelta(1)

        episode1 = Episode("episode1", 1, 1, before, "x", 1)
        episode2 = Episode("episode2", 1, 2, yesterday, "x", 2)
        episode3 = Episode("episode3", 1, 3, today, "x", 3)
        episode4 = Episode("episode4", 1, 4, tomorrow, "x", 4)

        self.db.add_episode(episode1, show)
        self.db.add_episode(episode2, show)
        self.db.add_episode(episode3, show)
        self.db.add_episode(episode4, show)

        self.db.commit()

        episodes = self.db.get_episodes(basedate=before, n_days=1)
        self.assertIn(episode1, episodes)
        self.assertIn(episode2, episodes)
        self.assertNotIn(episode3, episodes)
        self.assertNotIn(episode4, episodes)

        episodes = self.db.get_episodes(basedate=before, n_days=0)
        self.assertIn(episode1, episodes)
        self.assertNotIn(episode2, episodes)
        self.assertNotIn(episode3, episodes)
        self.assertNotIn(episode4, episodes)

        episodes = self.db.get_episodes(basedate=today, n_days=0)
        self.assertNotIn(episode1, episodes)
        self.assertNotIn(episode2, episodes)
        self.assertIn(episode3, episodes)
        self.assertNotIn(episode4, episodes)

        episodes = self.db.get_episodes(basedate=yesterday, n_days=2)
        self.assertNotIn(episode1, episodes)
        self.assertIn(episode2, episodes)
        self.assertIn(episode3, episodes)
        self.assertIn(episode4, episodes)

    def test_remove_before(self):

        show = self.db.add_show(Show("some show"))

        today = date.today()
        yesterday = today - timedelta(1)
        before = yesterday - timedelta(1)
        tomorrow = today + timedelta(1)

        episode1 = Episode("episode1", 1, 1, before, "x", 1)
        episode2 = Episode("episode2", 1, 2, yesterday, "x", 2)
        episode3 = Episode("episode3", 1, 3, today, "x", 3)
        episode4 = Episode("episode4", 1, 4, tomorrow, "x", 4)

        self.db.add_episode(episode1, show)
        self.db.add_episode(episode2, show)
        self.db.add_episode(episode3, show)
        self.db.add_episode(episode4, show)
        self.db.commit()

        episodes = self.db.get_episodes(basedate=before, n_days=10)
        self.assertIn(episode1, episodes)
        self.assertIn(episode2, episodes)
        self.assertIn(episode3, episodes)
        self.assertIn(episode4, episodes)

        self.db.remove_before(today)
        episodes = self.db.get_episodes(basedate=before, n_days=10)
        self.assertNotIn(episode1, episodes)
        self.assertNotIn(episode2, episodes)
        self.assertIn(episode3, episodes)
        self.assertIn(episode4, episodes)

    def test_remove_before_with_show(self):

        show1 = self.db.add_show(Show("some show", url="a"))
        show2 = self.db.add_show(Show("some other show", url="b"))

        today = date.today()
        yesterday = today - timedelta(1)

        episode1 = Episode("episode1", 1, 1, yesterday, "x", 1)
        episode2 = Episode("episode1", 1, 2, yesterday, "x", 1)
        episode3 = Episode("episode1", 1, 2, yesterday, "x", 1)

        self.db.add_episode(episode1, show1)
        self.db.add_episode(episode2, show1)
        self.db.add_episode(episode3, show2)

        self.db.commit()

        episodes = self.db.get_episodes(basedate=yesterday, n_days=10)
        self.assertIn(episode1, episodes)
        self.assertIn(episode2, episodes)
        self.assertIn(episode3, episodes)

        self.db.remove_before(today, show=show1)

        episodes = self.db.get_episodes(basedate=yesterday, n_days=10)
        self.assertNotIn(episode1, episodes)
        self.assertNotIn(episode2, episodes)
        self.assertIn(episode3, episodes)

    def test_duplicate_episodes(self):

        today = date.today()
        show = self.db.add_show(Show("some show"))
        self.assertEqual(0, len(self.db.get_episodes()))

        episode1 = Episode("e", 1, 1, today, "x", 1)
        self.db.add_episode(episode1, show)
        self.db.commit()

        episodes = self.db.get_episodes()
        self.assertEqual(1, len(episodes))
        self.assertIn(episode1, episodes)

        episode2 = Episode("f", 1, 1, today, "x", 1)
        self.db.add_episode(episode2, show)
        self.db.commit()

        episodes = self.db.get_episodes()
        self.assertEqual(1, len(episodes))
        self.assertIn(episode2, episodes)

    def test_clear(self):

        today = date.today()
        show = self.db.add_show(Show("some show", url="urlX"))
        self.assertEqual(0, len(self.db.get_episodes()))

        episode1 = Episode("e", 1, 1, today, "x", 1)
        episode2 = Episode("e", 1, 2, today, "x", 1)
        episode3 = Episode("e", 1, 3, today, "x", 1)
        episode4 = Episode("e", 1, 3, today, "x", 1)
        episode5 = Episode("e", 1, 4, today, "x", 1)

        self.db.add_episode(episode1, show)
        self.db.add_episode(episode2, show)
        self.db.add_episode(episode3, show)
        self.db.commit()

        episodes = self.db.get_episodes()
        self.assertEqual(3, len(episodes))
        self.assertIn(episode1, episodes)
        self.assertIn(episode2, episodes)
        self.assertIn(episode3, episodes)

        self.db.clear()
        self.assertEqual(0, len(self.db.get_episodes()))

        self.db.add_episode(episode4, show)
        self.db.add_episode(episode5, show)
        self.db.commit()

        episodes = self.db.get_episodes()
        self.assertEqual(2, len(episodes))
        self.assertIn(episode4, episodes)
        self.assertIn(episode5, episodes)

    def test_using_existing_database(self):

        path = mktemp()
        self.tempfiles.append(path)

        db = Database(path)
        self.assertEqual(len(db.get_shows()), 0)
        db.close()

        db = Database(path)
        self.assertEqual(len(db.get_shows()), 0)
        db.close()

    def test_set_get_schema_version(self):

        self.assertEqual(self.db.get_schema_version(), 4)

        self.db.set_schema_version(1)
        self.assertEqual(self.db.get_schema_version(), 1)

        self.db.set_schema_version(2)
        self.assertEqual(self.db.get_schema_version(), 2)

    def test_get_expired_shows(self):

        then = date(2017, 6, 4)

        # show1 -> running
        show1 = self.db.add_show(Show("1", url="1"))
        show1.updated = then
        show1.status = Show.RUNNING

        # show2 -> paused
        show2 = self.db.add_show(Show("2", url="2"))
        show2.updated = then
        show2.status = Show.SUSPENDED

        # show3 -> ended
        show3 = self.db.add_show(Show("3", url="3"))
        show3.updated = then
        show3.status = Show.ENDED

        self.db.commit()

        # all shows updated today, nothing expired
        shows = self.db.get_expired_shows(today=then)
        self.assertNotIn(show1, shows)
        self.assertNotIn(show2, shows)
        self.assertNotIn(show3, shows)

        # all shows updated 2 days ago, still nothing expired
        shows = self.db.get_expired_shows(today=then + timedelta(2))
        self.assertNotIn(show1, shows)
        self.assertNotIn(show2, shows)
        self.assertNotIn(show3, shows)

        # all shows updated 3 days ago, show1 should be expired
        shows = self.db.get_expired_shows(today=then + timedelta(3))
        self.assertIn(show1, shows)
        self.assertNotIn(show2, shows)
        self.assertNotIn(show3, shows)

        # all shows updated 8 days ago, shows 1 and 2 should be expired
        shows = self.db.get_expired_shows(today=then + timedelta(8))
        self.assertIn(show1, shows)
        self.assertIn(show2, shows)
        self.assertNotIn(show3, shows)

        # all shows updated 15 days ago, all shows should be expired
        shows = self.db.get_expired_shows(today=then + timedelta(15))
        self.assertIn(show1, shows)
        self.assertIn(show2, shows)
        self.assertIn(show3, shows)

        # disabled shows never expire
        show1.enabled = False
        show2.enabled = False
        show3.enabled = False
        self.db.commit()

        shows = self.db.get_expired_shows(today=then + timedelta(15))
        self.assertNotIn(show1, shows)
        self.assertNotIn(show2, shows)
        self.assertNotIn(show3, shows)

    def test_get_enabled_shows(self):

        show1 = self.db.add_show(Show("1", url="1"))
        show1.enabled = False

        show2 = self.db.add_show(Show("2", url="2"))
        self.db.commit()

        shows = self.db.get_enabled_shows()
        self.assertNotIn(show1, shows)
        self.assertIn(show2, shows)
