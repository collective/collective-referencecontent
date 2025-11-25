from collective.referencecontent.content.reference_content import IReferenceContent
from plone import api
from plone.indexer.interfaces import IIndexableObject
from plone.indexer.interfaces import IIndexableObjectWrapper
from plone.indexer.wrapper import IndexableObjectWrapper
from Products.ZCatalog.interfaces import IZCatalog
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer


ATTRS_TO_KEEP = [
    "UID",
    "id",
    "allowedRolesAndUsers",
    "getId",
    "object_provides",
    "path",
    "getPhysicalPath",
]


@implementer(IIndexableObject, IIndexableObjectWrapper)
@adapter(IReferenceContent, IZCatalog)
class ReferenceContentIndexableWrapper(IndexableObjectWrapper):
    """Makes CTProxy behave like its target during indexing."""

    def __getattr__(self, name):
        """
        Copy indexes/metadata from the proxied content, except a subset.
        """
        context = self._getWrappedObject()
        item = context.get_proxied_content()

        if not item:
            # item has been deleted, so just return the default behavior
            return super().__getattr__(name)

        catalog = api.portal.get_tool(name="portal_catalog")
        proxied_content = queryMultiAdapter((item, catalog), IIndexableObject)

        if name in ATTRS_TO_KEEP or not proxied_content:
            return super().__getattr__(name)

        return getattr(proxied_content, name)
