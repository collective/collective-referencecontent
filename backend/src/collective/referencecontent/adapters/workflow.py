from collective.referencecontent.content.reference_content import IReferenceContent
from plone.base.interfaces import IWorkflowChain
from Products.CMFCore.interfaces import IWorkflowTool
from Products.CMFPlone.workflow import ToolWorkflowChain
from zope.component import adapter
from zope.interface import implementer


@adapter(IReferenceContent, IWorkflowTool)
@implementer(IWorkflowChain)
def ProxyWorkflowChain(ob, tool):
    proxied_content = ob.get_proxied_content()
    if not proxied_content:
        return ToolWorkflowChain(ob, tool)

    return tool.getChainFor(proxied_content)
