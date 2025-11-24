import React from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import { useSelector } from 'react-redux';
import { useLocation } from 'react-router-dom';
import { defineMessages, useIntl } from 'react-intl';
import Toast from '@plone/volto/components/manage/Toast/Toast';
import { flattenToAppURL } from '@plone/volto/helpers/Url/Url';
import useDeepCompareEffect from 'use-deep-compare-effect';

const messages = defineMessages({
  referenceOfTitle: {
    id: 'reference-content-toast-title',
    defaultMessage: 'This is a reference content',
  },
  referenceOfText: {
    id: 'reference-content-toast-text',
    defaultMessage: 'Original content is {title}',
  },
});

const ReferenceContentToastsFactory = (props) => {
  const intl = useIntl();
  const pathname = useLocation().pathname;
  const lang = useSelector((state) => state.intl.locale);
  const { content } = props;
  const title = content?.title;
  const data = content?.proxied_content || [];
  const proxied_content = data.length === 1 ? data[0] : null;
  const actions = content?.['@components']?.actions?.object || [];
  const canEdit = actions.some((item) => item.id === 'edit');

  useDeepCompareEffect(() => {
    if (proxied_content && canEdit) {
      const toastMessage = messages.referenceOfText;
      const toastLink = (
        <Link to={flattenToAppURL(proxied_content['@id'])}>
          {proxied_content?.title}
        </Link>
      );

      if (toast.isActive('referenceOfInfo')) {
        toast.update('referenceOfInfo', {
          render: (
            <Toast
              info
              title={intl.formatMessage(messages.referenceOfTitle)}
              content={intl.formatMessage(toastMessage, {
                title: toastLink,
              })}
            />
          ),
        });
      } else {
        toast.info(
          <Toast
            info
            title={intl.formatMessage(messages.referenceOfTitle)}
            content={intl.formatMessage(toastMessage, {
              title: toastLink,
            })}
          />,
          {
            toastId: 'referenceOfInfo',
            autoClose: false,
            closeButton: false,
            transition: null,
          },
        );
      }
    }
    if (!proxied_content || !canEdit) {
      if (toast.isActive('referenceOfInfo')) {
        toast.dismiss('referenceOfInfo');
      }
    }
  }, [pathname, content, title, proxied_content, intl, lang]);

  return null;
};

export default ReferenceContentToastsFactory;
