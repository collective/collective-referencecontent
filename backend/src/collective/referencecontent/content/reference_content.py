from collective.referencecontent import _
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Item
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope.interface import implementer


class IReferenceContent(model.Schema):
    """Marker interface and Dexterity Python Schema for ReferenceContent"""

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
        pattern_options={"maximumSelectionSize": 1},
    )


@implementer(IReferenceContent)
class ReferenceContent(Item):
    """Content-type class for ReferenceContent"""

    def Title(self):
        if self.proxied_content:
            return self.proxied_content[0].to_object.Title()
        return super().Title()
