import React, { useEffect } from 'react'
import * as GovUK from 'govuk-react'
import { useTranslation } from 'next-i18next'

export const Success = (props: { referenceNumber: string }) => {
  const { t } = useTranslation(['screens'])

  useEffect(() => {
    localStorage.removeItem('qs')
  }, [])

  return (
    <div data-cy="success">
      <GovUK.Panel title={t('Success.header')}>
        {t('Success.title')}
        <br />
        <strong>{props.referenceNumber}</strong>
      </GovUK.Panel>

      <GovUK.Paragraph>{t('Success.description') as string}</GovUK.Paragraph>
    </div>
  )
}