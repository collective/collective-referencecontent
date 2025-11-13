from collective.referencecontent.content.reference_content import IReferenceContent
from collective.referencecontent.interfaces import IBrowserLayer
from plone.dexterity.utils import iterSchemata
from plone.restapi.interfaces import ISerializeToJson

# from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.dxcontent import SerializeToJson as DXSerializeToJson

# from plone.restapi.serializer.summary import DefaultJSONSummarySerializer
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer

import logging


logger = logging.getLogger(__name__)


@implementer(ISerializeToJson)
@adapter(IReferenceContent, IBrowserLayer)
class SerializeToJson(DXSerializeToJson):
    def __call__(self, version=None, include_items=True, include_expansion=True):
        base = super().__call__(version, include_items, include_expansion)
        proxied_content = self.context.get_proxied_content()
        if not proxied_content:
            return base
        proxied = getMultiAdapter((proxied_content, self.request), ISerializeToJson)(
            version=version,
            include_items=include_items,
            include_expansion=include_expansion,
        )
        # use base value for some attributes like those that are structural
        # (path, id, actions, ...)
        for attr in ["@components", "UID", "@id", "id", "@type", "lock", "parent"]:
            if attr in base:
                proxied[attr] = base[attr]
        # use base value for the attributes explictely definied in the schema
        for schema in iterSchemata(self.context):
            # skip schema that we can fetch from original (evaluate to
            # remove some behaviors from the CT)
            if schema.getName() in [
                "IBasic",
                "IAllowDiscussion",
                "IExcludeFromNavigation",
                "IShortName",
                "IOwnership",
                "IPublication",
                "ICategorization",
            ]:
                logger.debug("skipping", schema.getName())
                continue
            for attr in schema.names():
                if attr in base:
                    proxied[attr] = base[attr]
        return proxied
