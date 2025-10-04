import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Controller, type SubmitHandler, useForm } from "react-hook-form"

import {
  Button,
  DialogActionTrigger,
  DialogRoot,
  DialogTrigger,
  Flex,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useState } from "react"
import { FaEdit } from "react-icons/fa"

import { type ExchangePublic, type ExchangeUpdate, ExchangesService } from "@/client"
import type { ApiError } from "@/client/core/ApiError"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import { Checkbox } from "../ui/checkbox"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "../ui/dialog"
import { Field } from "../ui/field"

interface EditExchangeProps {
  exchange: ExchangePublic
}

const EditExchange = ({ exchange }: EditExchangeProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    control,
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ExchangeUpdate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: exchange,
  })

  const mutation = useMutation({
    mutationFn: (data: ExchangeUpdate) =>
      ExchangesService.updateExchange({ exchangeId: exchange.id, requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Exchange updated successfully.")
      reset()
      setIsOpen(false)
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["exchanges"] })
    },
  })

  const onSubmit: SubmitHandler<ExchangeUpdate> = (data) => {
    mutation.mutate(data)
  }

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm">
          <FaEdit fontSize="16px" />
          Edit Exchange
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Edit Exchange</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <Text mb={4}>Update the exchange details below.</Text>
            <VStack gap={4}>
              <Field
                invalid={!!errors.code}
                errorText={errors.code?.message}
                label="Exchange Code"
              >
                <Input
                  id="code"
                  {...register("code", {
                    maxLength: {
                      value: 20,
                      message: "Code must be 20 characters or less",
                    },
                  })}
                  placeholder="e.g., KIS, UPBIT"
                  type="text"
                />
              </Field>

              <Field
                invalid={!!errors.name}
                errorText={errors.name?.message}
                label="Exchange Name"
              >
                <Input
                  id="name"
                  {...register("name", {
                    maxLength: {
                      value: 100,
                      message: "Name must be 100 characters or less",
                    },
                  })}
                  placeholder="Exchange name"
                  type="text"
                />
              </Field>

              <Field
                invalid={!!errors.country}
                errorText={errors.country?.message}
                label="Country"
              >
                <Input
                  id="country"
                  {...register("country", {
                    maxLength: {
                      value: 50,
                      message: "Country must be 50 characters or less",
                    },
                  })}
                  placeholder="Country"
                  type="text"
                />
              </Field>

              <Field
                invalid={!!errors.timezone}
                errorText={errors.timezone?.message}
                label="Timezone"
              >
                <Input
                  id="timezone"
                  {...register("timezone", {
                    maxLength: {
                      value: 50,
                      message: "Timezone must be 50 characters or less",
                    },
                  })}
                  placeholder="e.g., UTC, Asia/Seoul"
                  type="text"
                />
              </Field>
            </VStack>

            <Flex mt={4} direction="column" gap={4}>
              <Controller
                control={control}
                name="is_active"
                render={({ field }) => (
                  <Field disabled={field.disabled} colorPalette="teal">
                    <Checkbox
                      checked={field.value}
                      onCheckedChange={({ checked }) => field.onChange(checked)}
                    >
                      Is active?
                    </Checkbox>
                  </Field>
                )}
              />
            </Flex>
          </DialogBody>

          <DialogFooter gap={2}>
            <DialogActionTrigger asChild>
              <Button
                variant="subtle"
                colorPalette="gray"
                disabled={isSubmitting}
              >
                Cancel
              </Button>
            </DialogActionTrigger>
            <Button variant="solid" type="submit" loading={isSubmitting}>
              Save
            </Button>
          </DialogFooter>
          <DialogCloseTrigger />
        </form>
      </DialogContent>
    </DialogRoot>
  )
}

export default EditExchange