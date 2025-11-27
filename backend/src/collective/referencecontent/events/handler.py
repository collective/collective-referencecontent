from Acquisition import aq_inner
from collective.referencecontent import _
from collective.referencecontent.interfaces import IBrowserLayer
from plone import api
from plone.api.exc import InvalidParameterError
from zc.relation.interfaces import ICatalog
from zExceptions import BadRequest
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

import logging


logger = logging.getLogger(__name__)


def get_references(context):
    catalog = getUtility(ICatalog)
    intids = getUtility(IIntIds)
    return catalog.findRelations(
        {
            "to_id": intids.getId(aq_inner(context)),
            "from_attribute": "proxied_content",
        }
    )


def on_modify(context, event):
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


def on_workflow_transition(context, event):
    """
    When the proxied content changes workflow state, update the reference
    content's workflow state to match.
    """
    if not IBrowserLayer.providedBy(context.REQUEST):
        return
    relations = get_references(context=context)
    for rel in relations:
        reference_obj = rel.from_object
        if reference_obj:
            with api.env.adopt_roles(["Manager"]):
                try:
                    api.content.transition(
                        obj=reference_obj, transition=event.transition.getId()
                    )
                except InvalidParameterError:
                    msg = _(
                        "error_workflow_transition_msg",
                        default='Unable to apply transition "${transition}" to object "${title}".',  # noqa
                        mapping={
                            "transition": event.transition.getId(),
                            "title": context.Title(),
                        },
                    )
                    logger.error(msg)
                    raise BadRequest(api.portal.translate(msg))


def on_create_reference_content(context, event):
    """
    When a ReferenceContent is created, set its workflow state to match the
    proxied content's state.
    """
    proxied_content = context.get_proxied_content()
    if not proxied_content:
        return

    workflow_tool = api.portal.get_tool(name="portal_workflow")
    proxied_state = workflow_tool.getInfoFor(
        proxied_content, "review_state", default=None
    )
    if not proxied_state:
        return

    with api.env.adopt_roles(["Manager"]):
        try:
            api.content.transition(obj=context, to_state=proxied_state)
        except InvalidParameterError:
            logger.error(
                "unable to set initial workflow state %s to object %s",
                proxied_state,
                context,
            )


def on_delete(context, event):
    """
    Do not delete an object if it is being referenced.
    """
    if not IBrowserLayer.providedBy(context.REQUEST):
        return
    has_references = False
    for ref in get_references(context):
        reference_obj = ref.from_object
        if reference_obj:
            has_references = True
            break
    if has_references:
        msg = _(
            "cannot_delete_msg",
            default='Cannot delete "${title}". '
            "It is referenced by Reference Content items.",
            mapping={"title": context.Title()},
        )
        raise BadRequest(api.portal.translate(msg))
