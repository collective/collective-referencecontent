from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from z3c.relationfield.relation import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

import pytest
import transaction


@pytest.mark.functional
def test_reference_content_proxies_catalog_metadata(request, functional):
    """Validate that the reference content indexes proxied metadata."""
    portal = functional["portal"]
    setRoles(portal, TEST_USER_ID, ["Manager"])
    catalog = api.portal.get_tool("portal_catalog")
    intids = getUtility(IIntIds)

    proxied_doc = api.content.create(
        container=portal,
        type="Document",
        id="proxied-doc",
        title="Proxied Document",
        description="This is the description.",
        subject=["one", "two"],
    )
    doc_intid = intids.getId(proxied_doc)

    reference_content = api.content.create(
        container=portal,
        type="ReferenceContent",
        id="reference-content",
        title="My Reference",
        proxied_content=[RelationValue(doc_intid)],
    )
    transaction.commit()

    brains = catalog(UID=reference_content.UID())
    assert len(brains) == 1

    brain = brains[0]

    # The brain's metadata should match the proxied document's data
    assert brain.Title == proxied_doc.title
    assert brain.Description == proxied_doc.description
    assert brain.Subject == proxied_doc.subject
    assert brain.portal_type == proxied_doc.portal_type

    # The id should be from the ReferenceContent itself
    assert brain.getId == "reference-content"
    assert reference_content.UID() == brain.UID
