from plone import api
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

import pytest
import transaction


@pytest.mark.functional
def test_reference_content_created_with_id_and_title_from_proxied_content(
    create_contents,
):
    """Validate that the reference content copy title and id from proxy."""
    proxied_doc, reference_content = create_contents

    assert reference_content.getId() == proxied_doc.getId() + "-1"
    assert reference_content.Title() == proxied_doc.Title()


@pytest.mark.functional
def test_reference_content_can_update_its_id(create_contents):
    proxied_doc, reference_content = create_contents

    assert reference_content.getId() == proxied_doc.getId() + "-1"

    reference_content.id = "my-new-id"
    transaction.commit()

    assert reference_content.getId() != proxied_doc.getId() + "-1"
    assert reference_content.getId() == "my-new-id"


@pytest.mark.functional
def test_reference_content_cant_update_its_title(create_contents):
    proxied_doc, reference_content = create_contents

    assert reference_content.title == proxied_doc.title
    assert reference_content.Title() == proxied_doc.Title()

    reference_content.title = "Foo"
    transaction.commit()

    assert reference_content.title != "Foo"
    assert reference_content.Title() != "Foo"
    assert reference_content.title == proxied_doc.Title()
    assert reference_content.Title() == proxied_doc.Title()


@pytest.mark.functional
def test_reference_content_proxies_catalog_metadata(
    create_contents, create_event_ref, catalog
):
    """Validate that the reference content indexes proxied metadata."""
    proxied_doc, reference_content = create_contents
    proxied_event, reference_event = create_event_ref

    doc_ref_brain = catalog(UID=reference_content.UID())[0]
    event_ref_brain = catalog(UID=reference_event.UID())[0]

    # The doc_ref_brain's metadata should match the proxied document's data
    assert doc_ref_brain.Title == proxied_doc.title
    assert doc_ref_brain.Description == proxied_doc.description
    assert doc_ref_brain.Subject == proxied_doc.subject
    assert doc_ref_brain.portal_type == proxied_doc.portal_type

    # The id should be from the ReferenceContent itself but with -1 (because they are in the same folder)
    assert doc_ref_brain.getId == proxied_doc.id + "-1"
    assert reference_content.UID() == doc_ref_brain.UID

    # reference event also have start/end metadata for events for example
    assert event_ref_brain.start == proxied_event.start
    assert event_ref_brain.end == proxied_event.end


@pytest.mark.functional
def test_reference_content_get_sync_also_on_status_change(create_contents, catalog):
    """"""
    proxied_doc, reference_content = create_contents

    brain = catalog(UID=reference_content.UID())[0]

    assert api.content.get_state(obj=proxied_doc) == "private"
    assert brain.review_state == api.content.get_state(obj=proxied_doc)

    api.content.transition(obj=proxied_doc, transition="publish")
    transaction.commit()

    brain = catalog(UID=reference_content.UID())[0]
    assert api.content.get_state(obj=proxied_doc) == "published"
    assert brain.review_state == api.content.get_state(obj=proxied_doc)


@pytest.mark.functional
def test_reference_content_get_sync_on_original_content_modify_event(
    create_contents, catalog
):
    """"""
    proxied_doc, reference_content = create_contents

    brain = catalog(UID=reference_content.UID())[0]

    assert brain.Title == proxied_doc.title
    assert brain.Description == proxied_doc.description
    assert brain.Subject == proxied_doc.subject
    assert proxied_doc.subject == ("one", "two")

    proxied_doc.subject = ()

    notify(ObjectModifiedEvent(proxied_doc))
    transaction.commit()

    brain = catalog(UID=reference_content.UID())[0]
    assert brain.Subject == proxied_doc.subject
    assert proxied_doc.subject == ()
