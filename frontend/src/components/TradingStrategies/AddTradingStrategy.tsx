import {
  Button,
  Input,
  NativeSelectField,
  NativeSelectRoot,
  Textarea,
} from "@chakra-ui/react"
import { type SubmitHandler, useForm } from "react-hook-form"

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

interface TradingStrategyForm {
  name: string
  strategy_type: string
  description?: string
  config: string
  is_active: boolean
}

interface AddTradingStrategyProps {
  isOpen: boolean
  onClose: () => void
}

const AddTradingStrategy = ({ isOpen, onClose }: AddTradingStrategyProps) => {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<TradingStrategyForm>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      strategy_type: "GRID",
      is_active: false,
      config: "{}",
    },
  })

  const onSubmit: SubmitHandler<TradingStrategyForm> = async (data) => {
    // TODO: API 연동
    console.log("전략 추가:", data)

    // 임시: config JSON 파싱 검증
    try {
      JSON.parse(data.config)
    } catch (e) {
      console.error("Invalid JSON config:", e)
      return
    }

    // 성공 처리
    handleClose()
  }

  const handleClose = () => {
    reset()
    onClose()
  }

  return (
    <DialogRoot open={isOpen} onOpenChange={handleClose} size="lg">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>매매 전략 추가</DialogTitle>
        </DialogHeader>
        <DialogCloseTrigger />
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogBody pb={6}>
            <Field
              label="전략 이름"
              required
              invalid={!!errors.name}
              errorText={errors.name?.message}
            >
              <Input
                {...register("name", {
                  required: "전략 이름을 입력해주세요",
                })}
                type="text"
                placeholder="예: 비트코인 그리드 전략"
              />
            </Field>

            <Field
              mt={4}
              label="전략 타입"
              required
              invalid={!!errors.strategy_type}
              errorText={errors.strategy_type?.message}
            >
              <NativeSelectRoot>
                <NativeSelectField
                  {...register("strategy_type", {
                    required: "전략 타입을 선택해주세요",
                  })}
                >
                  <option value="GRID">그리드 (Grid Trading)</option>
                  <option value="REBALANCING">리밸런싱 (Rebalancing)</option>
                  <option value="DCA">적립식 매수 (DCA)</option>
                </NativeSelectField>
              </NativeSelectRoot>
            </Field>

            <Field
              mt={4}
              label="설명"
              invalid={!!errors.description}
              errorText={errors.description?.message}
            >
              <Textarea
                {...register("description")}
                placeholder="전략에 대한 설명을 입력하세요 (선택사항)"
                rows={3}
              />
            </Field>

            <Field
              mt={4}
              label="전략 설정 (JSON)"
              required
              invalid={!!errors.config}
              errorText={errors.config?.message}
              helperText="JSON 형식으로 전략 설정을 입력하세요"
            >
              <Textarea
                {...register("config", {
                  required: "전략 설정을 입력해주세요",
                  validate: (value) => {
                    try {
                      JSON.parse(value)
                      return true
                    } catch {
                      return "올바른 JSON 형식이 아닙니다"
                    }
                  },
                })}
                placeholder='{"grid_count": 10, "price_range": [50000, 60000]}'
                rows={6}
                fontFamily="mono"
                fontSize="sm"
              />
            </Field>

            <Field mt={4} label="활성화 상태">
              <NativeSelectRoot>
                <NativeSelectField {...register("is_active")}>
                  <option value="false">비활성</option>
                  <option value="true">활성</option>
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

export default AddTradingStrategy
