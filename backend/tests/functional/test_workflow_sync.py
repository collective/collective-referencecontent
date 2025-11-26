from plone import api
from plone.app.testing import login
from plone.app.testing import logout

import pytest


@pytest.mark.functional
def test_reference_content_by_default_have_default_wf(
    portal,
):
    wf_tool = api.portal.get_tool(name="portal_workflow")
    assert wf_tool.getChainForPortalType("ReferenceContent") == (
        "simple_publication_workflow",
    )


@pytest.mark.functional
def test_reference_content_keep_default_wf_with_contents_with_default_wf(
    create_contents,
):
    """"""
    proxied_doc, reference_content = create_contents
    wf_tool = api.portal.get_tool(name="portal_workflow")

    assert wf_tool.getChainFor(reference_content) == ("simple_publication_workflow",)
    assert wf_tool.getChainFor(reference_content) == wf_tool.getChainFor(proxied_doc)


@pytest.mark.functional
def test_reference_content_inherit_wf_from_proxied_content(
    create_event_ref,
):
    """"""
    wf_tool = api.portal.get_tool(name="portal_workflow")
    wf_tool.setChainForPortalTypes(["Event"], "intranet_workflow")

    assert wf_tool.getChainForPortalType("ReferenceContent") == (
        "simple_publication_workflow",
    )
    assert wf_tool.getChainForPortalType("Event") == ("intranet_workflow",)

    proxied_event, reference_content = create_event_ref
    assert wf_tool.getChainFor(reference_content) == ("intranet_workflow",)
    assert wf_tool.getChainFor(reference_content) == wf_tool.getChainFor(proxied_event)


@pytest.mark.functional
def test_when_change_state_from_proxied_content_reference_content_also_change_state(
    create_contents,
):
    """"""
    proxied_doc, reference_content = create_contents

    assert api.content.get_state(obj=proxied_doc) == "private"
    assert api.content.get_state(obj=reference_content) == "private"

    api.content.transition(obj=proxied_doc, transition="publish")

    assert api.content.get_state(obj=proxied_doc) == "published"
    assert api.content.get_state(obj=reference_content) == "published"


@pytest.mark.functional
def test_when_a_reviewer_update_proxied_content_state_and_proxies_will_be_synced_also_if_he_dont_have_permissions(
    manager_portal, create_contents, additional_user
):
    """
    plone_workflow is the most complex workflow with different permissions in various transitions
    """
    wf_tool = api.portal.get_tool(name="portal_workflow")
    wf_tool.setChainForPortalTypes(["Document"], "plone_workflow")

    proxied_doc, reference_content = create_contents

    assert wf_tool.getChainFor(proxied_doc) == ("plone_workflow",)
    assert wf_tool.getChainFor(reference_content) == ("plone_workflow",)

    # default state is "visible" aka "Public Draft"
    assert api.content.get_state(obj=proxied_doc) == "visible"
    assert api.content.get_state(obj=reference_content) == "visible"

    user_id = additional_user["id"]

    api.user.grant_roles(username=user_id, roles=["Manager"], obj=proxied_doc)

    # check user roles on both objects
    assert set(api.user.get_roles(user_id, obj=proxied_doc)) == {
        "Authenticated",
        "Member",
        "Manager",
    }
    assert set(api.user.get_roles(username=user_id, obj=reference_content)) == {
        "Authenticated",
        "Member",
    }

    # now login as additional_user and try to change state of proxied_doc
    logout()
    login(manager_portal, user_id)

    api.content.transition(obj=proxied_doc, transition="publish")
    assert api.content.get_state(obj=proxied_doc) == "published"
    assert api.content.get_state(obj=reference_content) == "published"

    # "Request review" is the permission needed for "retract" transition, current
    # user hasn't this permission on reference_content but has it on proxied_doc
    assert not api.user.has_permission(
        permission="Request review", username=user_id, obj=reference_content
    )
    assert api.user.has_permission(
        permission="Request review", username=user_id, obj=proxied_doc
    )
    api.content.transition(obj=proxied_doc, transition="retract")
    assert api.content.get_state(obj=proxied_doc) == "visible"
    assert api.content.get_state(obj=reference_content) == "visible"

    api.content.transition(obj=proxied_doc, transition="hide")
    assert api.content.get_state(obj=proxied_doc) == "private"
    assert api.content.get_state(obj=reference_content) == "private"
