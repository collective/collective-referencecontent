from collective.referencecontent.content.reference_content import IReferenceContent
from collective.referencecontent.interfaces import IBrowserLayer
from plone.dexterity.utils import iterSchemata
from plone.restapi.interfaces import ISerializeToJson

# from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.dxcontent import SerializeToJson as DXSerializeToJson
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer


@implementer(ISerializeToJson)
@adapter(IReferenceContent, IBrowserLayer)
class SerializeToJson(DXSerializeToJson):
    def __call__(self, version=None, include_items=True, include_expansion=True):
        base = super().__call__(version, include_items, include_expansion)
        proxied_content = (
            self.context.proxied_content and self.context.proxied_content[0].to_object
        )
        if proxied_content:
            proxied = getMultiAdapter(
                (proxied_content, self.request), ISerializeToJson
            )(
                version=version,
                include_items=include_items,
                include_expansion=include_expansion,
            )
            # TODO: skip some attributes like those that are structural (path, actions,
            #       ...) and some explicitly defined in the schema
            for attr in ["@components", "UID", "id", "@type", "lock", "parent"]:
                if attr in base:
                    proxied[attr] = base[attr]
                # else:
                #     print(f"missing {attr}")
            for schema in iterSchemata(self.context):
                # skip schema that we can fetch from original (evaluate to
                # remove behaviors from the CT)
                if schema.getName() in [
                    "IBasic",
                    "IAllowDiscussion",
                    "IExcludeFromNavigation",
                    "IShortName",
                    "IOwnership",
                    "IPublication",
                    "ICategorization",
                ]:
                    # print(f"skipping {schema.getName()}")
                    continue
                for attr in schema.names():
                    if attr in base:
                        proxied[attr] = base[attr]
                    # else:
                    #     print(f"missing {attr}")
            return proxied
            # for (k, v) in proxied.items():
            #     if k in ["layout"]:
            #         base[k] = v
            #     elif k not in base:
            #         base[k] = v
            #     else:
            #         print(f"duplicate {k}")
            # return base
        else:
            return base
