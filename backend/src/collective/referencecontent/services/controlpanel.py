# -*- coding: utf-8 -*-
from collective.referencecontent.controlpanels.settings import IReferenceContentSettings
from collective.referencecontent.interfaces import IBrowserLayer
from plone.restapi.controlpanels import RegistryConfigletPanel
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@adapter(Interface, IBrowserLayer)
@implementer(IReferenceContentSettings)
class ReferenceContentSettingsControlpanel(RegistryConfigletPanel):
    schema = IReferenceContentSettings
    configlet_id = "ReferenceContentSettings"
    configlet_category_id = "Products"
    schema_prefix = None
