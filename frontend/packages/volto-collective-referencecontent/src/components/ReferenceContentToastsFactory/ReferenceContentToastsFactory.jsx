import React from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import { useSelector } from 'react-redux';
import { useLocation } from 'react-router-dom';
import { defineMessages, useIntl } from 'react-intl';
import Toast from '@plone/volto/components/manage/Toast/Toast';
import { flattenToAppURL } from '@plone/volto/helpers/Url/Url';
// import FormattedDate from '@plone/volto/components/theme/FormattedDate/FormattedDate';
import useDeepCompareEffect from 'use-deep-compare-effect';

const messages = defineMessages({
  thisIsAReferenceOf: {
    id: 'This is a reference of {title}',
    defaultMessage: 'This is a reference of {title}',
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

  useDeepCompareEffect(() => {
    if (proxied_content) {
      let toastMessage, toastTitle;
      toastMessage = messages.thisIsAReferenceOf;
      toastTitle = (
        <Link to={flattenToAppURL(proxied_content['@id'])}>
          {proxied_content?.title}
        </Link>
      );

      if (toast.isActive('referenceOfInfo')) {
        toast.update('referenceOfInfo', {
          render: (
            <Toast
              i
              title={intl.formatMessage(toastMessage, {
                title: toastTitle,
              })}
              //   content={intl.formatMessage(messages.workingCopyCreatedBy, {
              //     creator: working_copy?.creator_name,
              //     date: (
              //       <FormattedDate
              //         date={working_copy?.created}
              //         format={dateOptions}
              //       />
              //     ),
              //   })}
            />
          ),
        });
      } else {
        toast.info(
          <Toast
            info
            title={intl.formatMessage(toastMessage, {
              title: toastTitle,
            })}
            // content={intl.formatMessage(messages.workingCopyCreatedBy, {
            //   creator: working_copy?.creator_name,
            //   date: (
            //     <FormattedDate
            //       date={working_copy?.created}
            //       format={dateOptions}
            //     />
            //   ),
            // })}
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
    if (!proxied_content) {
      if (toast.isActive('referenceOfInfo')) {
        toast.dismiss('referenceOfInfo');
      }
    }
  }, [pathname, content, title, proxied_content, intl, lang]);

  return null;
};

export default ReferenceContentToastsFactory;
