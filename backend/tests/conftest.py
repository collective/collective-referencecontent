from collective.referencecontent.testing import ACCEPTANCE_TESTING
from collective.referencecontent.testing import FUNCTIONAL_TESTING
from collective.referencecontent.testing import INTEGRATION_TESTING
from datetime import datetime
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from pytest_plone import fixtures_factory
from z3c.relationfield.relation import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

import pytest
import transaction


pytest_plugins = ["pytest_plone"]


globals().update(
    fixtures_factory((
        (ACCEPTANCE_TESTING, "acceptance"),
        (FUNCTIONAL_TESTING, "functional"),
        (INTEGRATION_TESTING, "integration"),
    ))
)


@pytest.fixture
def manager_portal(functional):
    """Portal with Manager role."""
    portal = functional["portal"]
    setRoles(portal, TEST_USER_ID, ["Manager"])
    return portal


@pytest.fixture
def intids():
    """Utility IntIds."""
    return getUtility(IIntIds)


@pytest.fixture
def catalog():
    """Portal catalog."""
    return api.portal.get_tool("portal_catalog")


@pytest.fixture
def create_contents(manager_portal, intids):
    """Helper that creates a proxied content and returns (obj, intid)."""

    proxied_doc = api.content.create(
        container=manager_portal,
        type="Document",
        title="Proxied Document",
        description="This is the description.",
        subject=["one", "two"],
    )
    doc_intid = intids.getId(proxied_doc)

    reference_content = api.content.create(
        container=manager_portal,
        type="ReferenceContent",
        title="",
        proxied_content=[RelationValue(doc_intid)],
    )
    transaction.commit()
    return proxied_doc, reference_content


@pytest.fixture
def create_event_ref(manager_portal, intids):
    """Helper that creates a proxied content and returns (obj, intid)."""

    proxied_event = api.content.create(
        container=manager_portal,
        type="Event",
        title="Proxied Event",
        start=datetime(2024, 4, 22, 12, 0),
        end=datetime(2024, 4, 22, 12, 0),
    )
    event_intid = intids.getId(proxied_event)

    reference_event = api.content.create(
        container=manager_portal,
        type="ReferenceContent",
        title="",
        proxied_content=[RelationValue(event_intid)],
    )
    transaction.commit()
    return proxied_event, reference_event
