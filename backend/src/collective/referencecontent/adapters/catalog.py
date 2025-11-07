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

    @property
    def proxied_content(self):
        context = self._getWrappedObject()
        proxied_ref = getattr(context, "proxied_content", None)
        if not proxied_ref:
            return None
        catalog = api.portal.get_tool(name="portal_catalog")
        proxied_content = proxied_ref[0].to_object
        if proxied_content:
            return queryMultiAdapter((proxied_content, catalog), IIndexableObject)
        return None

    def __getattr__(self, name):
        """
        Copy indexes/metadata from the proxied content, except a subset.
        """
        if name in ATTRS_TO_KEEP or not self.proxied_content:
            return super().__getattr__(name)

        return getattr(self.proxied_content, name)
