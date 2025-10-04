import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Controller, type SubmitHandler, useForm } from "react-hook-form"

import { type ExchangeCreate, ExchangesService } from "@/client"
import type { ApiError } from "@/client/core/ApiError"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import {
  Button,
  DialogActionTrigger,
  DialogTitle,
  Flex,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useState } from "react"
import { FaPlus } from "react-icons/fa"
import { Checkbox } from "../ui/checkbox"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"

const AddExchange = () => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    control,
    register,
    handleSubmit,
    reset,
    formState: { errors, isValid, isSubmitting },
  } = useForm<ExchangeCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      code: "",
      name: "",
      country: "",
      timezone: "",
      is_active: true,
    },
  })

  const mutation = useMutation({
    mutationFn: (data: ExchangeCreate) =>
      ExchangesService.createExchange({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Exchange created successfully.")
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

  const onSubmit: SubmitHandler<ExchangeCreate> = (data) => {
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
        <Button value="add-exchange" my={4}>
          <FaPlus fontSize="16px" />
          Add Exchange
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Add Exchange</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <Text mb={4}>
              Fill in the form below to add a new exchange to the system.
            </Text>
            <VStack gap={4}>
              <Field
                required
                invalid={!!errors.code}
                errorText={errors.code?.message}
                label="Exchange Code"
              >
                <Input
                  id="code"
                  {...register("code", {
                    required: "Exchange code is required",
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
                required
                invalid={!!errors.name}
                errorText={errors.name?.message}
                label="Exchange Name"
              >
                <Input
                  id="name"
                  {...register("name", {
                    required: "Exchange name is required",
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
            <Button
              variant="solid"
              type="submit"
              disabled={!isValid}
              loading={isSubmitting}
            >
              Save
            </Button>
          </DialogFooter>
        </form>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default AddExchange