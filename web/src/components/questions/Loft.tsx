import React from 'react'
import { useTranslation } from 'next-i18next'
import { useForm, SubmitHandler } from 'react-hook-form'
import * as GovUK from 'govuk-react'
import { Button } from '@/components/ui/Button'
import { LoftType } from '@/types'

type Inputs = {
  loft: LoftType
}

const options: {
  label: string
  value: LoftType
  hint?: string
}[] = [
  {
    label: 'yes',
    value: 'yes'
  },
  {
    label: 'no',
    value: 'no'
  }
]

export const Loft = (props: {
  onSubmit: (v: LoftType) => void
  defaultValues?: {
    loft?: LoftType
  }
}) => {
  const { t } = useTranslation(['questionnaire'])

  const {
    register,
    handleSubmit,
    formState: { errors, submitCount }
  } = useForm<Inputs>({
    reValidateMode: 'onSubmit',
    defaultValues: props.defaultValues
  })

  const onSubmit: SubmitHandler<Inputs> = (data) => {
    props.onSubmit(data.loft)
  }

  const errorsToShow = Object.keys(errors)

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {!!errorsToShow?.length && (
        <GovUK.ErrorSummary
          heading={
            t('error-title', {
              ns: 'common'
            }) as string
          }
          description={
            t('error-message', {
              ns: 'common'
            }) as string
          }
        />
      )}

      <GovUK.Fieldset>
        <GovUK.Fieldset.Legend size="L">{t('Loft.title')}</GovUK.Fieldset.Legend>

        <GovUK.FormGroup error={submitCount > 0 && !!errors?.loft?.message}>
          <GovUK.Label mb={4}>
            {submitCount > 0 && errors?.loft?.message && (
              <GovUK.ErrorText>{errors?.loft.message}</GovUK.ErrorText>
            )}

            {options.map((option) => (
              <GovUK.Radio
                key={option.label}
                value={option.value}
                type="radio"
                {...register('loft', {
                  required: {
                    value: true,
                    message: t('form-required', {
                      ns: 'common'
                    })
                  }
                })}
              >
                {t(option.label, { ns: 'common' })}
              </GovUK.Radio>
            ))}
          </GovUK.Label>
        </GovUK.FormGroup>
      </GovUK.Fieldset>

      <Button type="submit">
        {
          t('continue', {
            ns: 'common'
          }) as string
        }
      </Button>
    </form>
  )
}
