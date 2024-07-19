# -*- coding: utf-8 -*-
from plone.indexer.decorator import indexer
from rer.externalnews.interfaces import IExternalNews


@indexer(IExternalNews)
def getRemoteUrl(obj):
    return getattr(obj, "externalUrl", "")
