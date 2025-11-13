from collective.referencecontent.content.reference_content import IReferenceContent
from collective.referencecontent.interfaces import IBrowserLayer
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from plone.restapi.services.workflow.info import WorkflowInfo as BaseWorkflowInfo
from zope.component import adapter
from zope.interface import implementer


@implementer(IExpandableElement)
@adapter(IReferenceContent, IBrowserLayer)
class WorkflowInfo(BaseWorkflowInfo):
    """
    Adapter for reference content
    """

    def __call__(self, expand=False):
        """
        Get original data, but override state title because it's not translated
        """
        result = super().__call__(expand=expand)
        if not result["workflow"].get("state", {}):
            # expander not expanded
            return result
        wftool = api.portal.get_tool(name="portal_workflow")
        try:
            proxied_content = self.context.get_proxied_content()
        except AttributeError:
            return result

        if not proxied_content:
            return result

        current_state_title = wftool.getTitleForStateOnType(
            result["workflow"]["state"]["id"],
            proxied_content.portal_type,
        )
        result["workflow"]["state"]["title"] = self.context.translate(
            current_state_title
        )
        return result


class WorkflowInfoService(Service):
    """Get workflow information"""

    def reply(self):
        info = WorkflowInfo(self.context, self.request)
        return info(expand=True)["workflow"]
