# -*- coding: utf-8 -*-
from plone import api

import logging


logger = logging.getLogger(__name__)


default_profile = "profile-rer.externalnews:default"


def to_1100(context):
    """ """
    logger.info("Upgrading rer.externalnews to version 1100")
    context.runImportStepFromProfile(default_profile, "repositorytool")
    context.runImportStepFromProfile(default_profile, "difftool")
    context.runImportStepFromProfile(default_profile, "typeinfo", run_dependencies=True)


def to_1200(context):
    """ """
    logger.info("Upgrading rer.externalnews to version 1200")
    brains = api.content.find(portal_type="ExternalNews")
    tot = len(brains)
    i = 0
    for brain in brains:
        i += 1
        if i % 100 == 0:
            logger.info(f"Progress: {i}/{tot}")

        news = brain.getObject()
        news.reindexObject(idxs=["getRemoteUrl"])
