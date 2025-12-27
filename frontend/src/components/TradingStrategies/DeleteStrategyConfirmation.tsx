import { Button, Text } from "@chakra-ui/react"

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

interface TradingStrategy {
  id: number
  name: string
  strategy_type: string
}

interface DeleteStrategyConfirmationProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void
  strategy: TradingStrategy | null
}

const DeleteStrategyConfirmation = ({
  isOpen,
  onClose,
  onConfirm,
  strategy,
}: DeleteStrategyConfirmationProps) => {
  if (!strategy) return null

  return (
    <DialogRoot open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>전략 삭제 확인</DialogTitle>
        </DialogHeader>
        <DialogCloseTrigger />
        <DialogBody pb={6}>
          <Text>
            정말로 <strong>"{strategy.name}"</strong> 전략을 삭제하시겠습니까?
          </Text>
          <Text mt={2} fontSize="sm" color="gray.600">
            이 작업은 되돌릴 수 없으며, 해당 전략과 연결된 모든 종목 매핑도
            함께 삭제됩니다.
          </Text>
        </DialogBody>
        <DialogFooter>
          <DialogActionTrigger asChild>
            <Button variant="outline" mr={3}>
              취소
            </Button>
          </DialogActionTrigger>
          <Button colorPalette="red" onClick={onConfirm}>
            삭제
          </Button>
        </DialogFooter>
      </DialogContent>
    </DialogRoot>
  )
}

export default DeleteStrategyConfirmation
