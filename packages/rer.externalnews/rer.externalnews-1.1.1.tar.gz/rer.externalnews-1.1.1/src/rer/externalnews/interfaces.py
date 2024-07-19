# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from rer.externalnews import _
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IRerExternalnewsLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IExternalNews(Interface):
    """Interfaccia per il content type: External News"""

    externalUrl = schema.TextLine(
        title=_("rer_externalnews_externalurl", default="External url"),
        description=_(
            "rer_ernews_externalurl_help",
            default="Insert a valid link to an external resource",
        ),
        default="",
        required=True,
    )

    externalSource = schema.TextLine(
        title=_("rer_externalnews_externalsource", default="Source"),
        description=_(
            "rer_externalnews_externalsource_help", default="Where the URL is from."
        ),
        default="",
        required=False,
    )
