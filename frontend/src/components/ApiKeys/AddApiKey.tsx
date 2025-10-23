import {
  Button,
  Input,
  NativeSelectField,
  NativeSelectRoot,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import {
  type ApiError,
  type UserApiKeyCreate,
  UserApiKeysService,
} from "@/client"
import {
  DialogActionTrigger,
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
} from "@/components/ui/dialog"
import { Field } from "@/components/ui/field"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

interface AddApiKeyProps {
  isOpen: boolean
  onClose: () => void
}

const AddApiKey = ({ isOpen, onClose }: AddApiKeyProps) => {
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<UserApiKeyCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      exchange_type: "UPBIT",
      is_demo: false,
    },
  })

  const mutation = useMutation({
    mutationFn: (data: UserApiKeyCreate) =>
      UserApiKeysService.createUserApiKey({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("API Key가 성공적으로 등록되었습니다.")
      queryClient.invalidateQueries({ queryKey: ["apiKeys"] })
      onClose()
      reset()
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
  })

  const onSubmit: SubmitHandler<UserApiKeyCreate> = async (data) => {
    mutation.mutate(data)
  }

  const handleClose = () => {
    reset()
    onClose()
  }

  return (
    <DialogRoot open={isOpen} onOpenChange={handleClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>API Key 추가</DialogTitle>
        </DialogHeader>
        <DialogCloseTrigger />
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogBody pb={6}>
            <Field
              label="거래소"
              required
              invalid={!!errors.exchange_type}
              errorText={errors.exchange_type?.message}
            >
              <NativeSelectRoot>
                <NativeSelectField
                  {...register("exchange_type", {
                    required: "거래소를 선택해주세요",
                  })}
                  placeholder="거래소 선택"
                >
                  <option value="UPBIT">업비트 (UPBIT)</option>
                  <option value="KIS">한국투자증권 (KIS)</option>
                  <option value="BINANCE">바이낸스 (BINANCE)</option>
                </NativeSelectField>
              </NativeSelectRoot>
            </Field>

            <Field
              mt={4}
              label="API Key"
              required
              invalid={!!errors.encrypted_api_key}
              errorText={errors.encrypted_api_key?.message}
            >
              <Input
                {...register("encrypted_api_key", {
                  required: "API Key를 입력해주세요",
                })}
                type="text"
                placeholder="API Key"
              />
            </Field>

            <Field
              mt={4}
              label="API Secret"
              required
              invalid={!!errors.encrypted_api_secret}
              errorText={errors.encrypted_api_secret?.message}
            >
              <Input
                {...register("encrypted_api_secret", {
                  required: "API Secret을 입력해주세요",
                })}
                type="password"
                placeholder="API Secret"
              />
            </Field>

            <Field
              mt={4}
              label="계좌번호"
              invalid={!!errors.account_number}
              errorText={errors.account_number?.message}
            >
              <Input
                {...register("account_number")}
                type="text"
                placeholder="계좌번호 (선택사항)"
              />
            </Field>

            <Field
              mt={4}
              label="별칭"
              invalid={!!errors.nickname}
              errorText={errors.nickname?.message}
            >
              <Input
                {...register("nickname")}
                type="text"
                placeholder="키 별칭 (선택사항)"
              />
            </Field>

            <Field mt={4} label="타입">
              <NativeSelectRoot>
                <NativeSelectField {...register("is_demo")}>
                  <option value="false">실전투자</option>
                  <option value="true">모의투자</option>
                </NativeSelectField>
              </NativeSelectRoot>
            </Field>
          </DialogBody>

          <DialogFooter>
            <DialogActionTrigger asChild>
              <Button variant="outline" mr={3} onClick={handleClose}>
                취소
              </Button>
            </DialogActionTrigger>
            <Button type="submit" loading={isSubmitting}>
              추가
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </DialogRoot>
  )
}

export default AddApiKey
