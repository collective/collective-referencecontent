import type { ConfigType } from '@plone/registry';
import ReferenceContentToastsFactory from "../components/ReferenceContentToastsFactory/ReferenceContentToastsFactory"
export default function install(config: ConfigType) {
  config.settings.appExtras = [
    ...(config.settings.appExtras || []),
    {match: "", component: ReferenceContentToastsFactory}
  ];
  return config;
}
