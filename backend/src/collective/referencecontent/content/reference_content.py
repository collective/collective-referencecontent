from collective.referencecontent import _
from collective.referencecontent.controlpanels.settings import IReferenceContentSettings
from plone import api
from plone.app.content.interfaces import INameFromTitle
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform import directives
from plone.autoform import directives as form
from plone.dexterity.content import Item
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope.interface import implementer
from zope.schema import TextLine


def get_selectable_types():
    return api.portal.get_registry_record(
        "referenceable_types", interface=IReferenceContentSettings, default=[]
    )


class IReferenceContent(model.Schema):
    """Marker interface and Dexterity Python Schema for ReferenceContent"""

    form.mode(title="hidden")
    title = TextLine(
        title=_("title", default="Title"),
        required=False,
    )
    proxied_content = RelationList(
        title=_("proxied_content", default="Proxied content"),
        value_type=RelationChoice(
            vocabulary="plone.app.vocabularies.Catalog",
        ),
        required=True,
        default=[],
    )

    directives.widget(
        "proxied_content",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options=lambda: {
            "maximumSelectionSize": 1,
            "selectableTypes": get_selectable_types(),
        },
    )


@implementer(IReferenceContent, INameFromTitle)
class ReferenceContent(Item):
    """Content-type class for ReferenceContent"""

    def Title(self):
        return self.title

    @property
    def title(self):
        """
        Title is set from proxied content
        """
        proxied_content = self.get_proxied_content()
        if proxied_content:
            return proxied_content.title
        return ""

    @title.setter
    def title(self, value):
        pass

    def get_proxied_content(self):
        """
        Return the proxied content object
        """
        proxied_ref = getattr(self, "proxied_content", [])
        if not proxied_ref:
            return None
        return proxied_ref[0].to_object
