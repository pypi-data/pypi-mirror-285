# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
)
from plone.testing import z2

import rer.externalnews


class RerExternalnewsLayer(PloneSandboxLayer):
    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=rer.externalnews)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "rer.externalnews:default")


RER_EXTERNALNEWS_FIXTURE = RerExternalnewsLayer()


RER_EXTERNALNEWS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(RER_EXTERNALNEWS_FIXTURE,), name="RerExternalnewsLayer:IntegrationTesting"
)


RER_EXTERNALNEWS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(RER_EXTERNALNEWS_FIXTURE,), name="RerExternalnewsLayer:FunctionalTesting"
)


RER_EXTERNALNEWS_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(RER_EXTERNALNEWS_FIXTURE, REMOTE_LIBRARY_BUNDLE_FIXTURE, z2.ZSERVER_FIXTURE),
    name="RerExternalnewsLayer:AcceptanceTesting",
)
