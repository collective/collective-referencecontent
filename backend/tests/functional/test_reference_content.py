from datetime import datetime
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

    proxied_event = api.content.create(
        container=portal,
        type="Event",
        id="proxied-even",
        title="Proxied Event",
        start=datetime(2024, 4, 22, 12, 0),
        end=datetime(2024, 4, 22, 12, 0),
    )
    event_intid = intids.getId(proxied_event)

    reference_content = api.content.create(
        container=portal,
        type="ReferenceContent",
        id="reference-content",
        title="My Reference",
        proxied_content=[RelationValue(doc_intid)],
    )
    reference_event = api.content.create(
        container=portal,
        type="ReferenceContent",
        id="reference-event",
        title="My Reference Event",
        proxied_content=[RelationValue(event_intid)],
    )
    transaction.commit()

    doc_ref_brain = catalog(UID=reference_content.UID())[0]
    event_ref_brain = catalog(UID=reference_event.UID())[0]

    # The doc_ref_brain's metadata should match the proxied document's data
    assert doc_ref_brain.Title == proxied_doc.title
    assert doc_ref_brain.Description == proxied_doc.description
    assert doc_ref_brain.Subject == proxied_doc.subject
    assert doc_ref_brain.portal_type == proxied_doc.portal_type

    # The id should be from the ReferenceContent itself
    assert doc_ref_brain.getId == "reference-content"
    assert reference_content.UID() == doc_ref_brain.UID

    # reference event also have start/end metadata
    assert event_ref_brain.start == proxied_event.start
    assert event_ref_brain.end == proxied_event.end
