# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.dxcontent import SerializeFolderToJson as Base
from rer.externalnews.interfaces import IExternalNews
from zope.component import adapter, getMultiAdapter
from zope.interface import implementer, Interface


@implementer(ISerializeToJson)
@adapter(IExternalNews, Interface)
class SerializeToJson(Base):
    def __call__(self, version=None, include_items=True):
        res = super(SerializeToJson, self).__call__(version, include_items)
        steps = self.get_steps()
        res["steps"] = steps
        res["remoteUrl"] = res["externalUrl"]
        return res

    def get_steps(self):
        query = {
            "path": {"depth": 1, "query": "/it".join(self.context.getPhysicalPath())},
            "sort_on": "getObjPositionInParent",
        }
        brains = api.content.find(**query)
        return getMultiAdapter((brains, self.request), ISerializeToJson)(
            fullobjects=True
        )["items"]
