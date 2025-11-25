from Acquisition import aq_inner
from collective.referencecontent.interfaces import IBrowserLayer
from contextlib import suppress
from plone import api
from plone.api.exc import InvalidParameterError
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


def get_references(context):
    catalog = getUtility(ICatalog)
    intids = getUtility(IIntIds)
    return catalog.findRelations(
        {
            "to_id": intids.getId(aq_inner(context)),
            "from_attribute": "proxied_content",
        }
    )


def onModify(context, event):
    """
    Reindex reference contents
    """
    if not IBrowserLayer.providedBy(context.REQUEST):
        return

    relations = get_references(context=context)
    for rel in relations:
        reference_obj = rel.from_object
        if reference_obj:
            reference_obj.reindexObject()


def onWorkflowTransition(context, event):
    if not IBrowserLayer.providedBy(context.REQUEST):
        return

    relations = get_references(context=context)
    for rel in relations:
        reference_obj = rel.from_object
        if reference_obj:
            with api.env.adopt_roles(["Reviewer"]):
                with suppress(InvalidParameterError):
                    api.content.transition(
                        obj=reference_obj, to_state=event.new_state.id
                    )
