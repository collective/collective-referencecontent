from collective.referencecontent import _
from plone.app.registry.browser import controlpanel
from plone.restapi.controlpanels.interfaces import IControlpanel
from zope import schema


class IReferenceContentSettings(IControlpanel):
    """
    Schema interface
    """

    referenceable_types = schema.List(
        title=_("referenceable_types_label", default="Referenceable portal types"),
        description=_(
            "referenceable_types_help",
            default="Select a list of portal types that can be referenced."
            " Leave empty to allow all types.",
        ),
        required=False,
        default=[],
        missing_value=[],
        value_type=schema.Choice(vocabulary="plone.app.vocabularies.PortalTypes"),
    )


class ReferenceContentSettingsForm(controlpanel.RegistryEditForm):
    schema = IReferenceContentSettings
    label = _("reference_content_settings_label", default="Reference Content")


class ReferenceContentSettings(controlpanel.ControlPanelFormWrapper):
    form = ReferenceContentSettingsForm
