#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2020 FABRIC Testbed
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#
# Author: Komal Thareja (kthare10@renci.org)
import unittest
import time
from fabric_cf.actor.core.apis.abc_database import ABCDatabase
from fabric_cf.actor.core.common.constants import Constants
from fabric_cf.actor.core.plugins.substrate.db.substrate_actor_database import SubstrateActorDatabase
from fabric_cf.actor.test.base_test_case import BaseTestCase


class SubstrateTestBase(BaseTestCase, unittest.TestCase):
    from fabric_cf.actor.core.container.globals import Globals
    Globals.config_file = "./config/config.test.yaml"
    Constants.SUPERBLOCK_LOCATION = './state_recovery.lock'

    from fabric_cf.actor.core.container.globals import GlobalsSingleton
    GlobalsSingleton.get().start(force_fresh=True)
    while not GlobalsSingleton.get().start_completed:
        time.sleep(0.0001)

    def make_actor_database(self) -> ABCDatabase:
        db = SubstrateActorDatabase(user=self.db_user, password=self.db_pwd, database=self.db_name, db_host=self.db_host,
                                    logger=self.logger)
        return db

    def test_actor(self):
        actor = self.get_actor()
        self.assertIsNotNone(actor)
