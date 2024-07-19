# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles, TEST_USER_ID
from rer.externalnews.testing import RER_EXTERNALNEWS_INTEGRATION_TESTING

import unittest


class ExternalNewsIntegrationTest(unittest.TestCase):
    layer = RER_EXTERNALNEWS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_getRemoteUrl_metadata_set(self):
        news = api.content.create(
            container=self.portal,
            type="ExternalNews",
            id="ExternalNews",
            externalUrl="http://www.plone.org",
        )

        res = api.content.find(UID=news.UID())[0]
        self.assertEqual(res.getRemoteUrl, news.externalUrl)
