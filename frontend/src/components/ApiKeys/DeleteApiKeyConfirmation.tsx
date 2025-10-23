import { Button, ButtonGroup, Text } from "@chakra-ui/react"

import type { UserApiKeyPublic } from "@/client"
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

interface DeleteApiKeyConfirmationProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void
  apiKey: UserApiKeyPublic | null
}

const DeleteApiKeyConfirmation = ({
  isOpen,
  onClose,
  onConfirm,
  apiKey,
}: DeleteApiKeyConfirmationProps) => {
  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      role="alertdialog"
      placement="center"
      open={isOpen}
      onOpenChange={onClose}
    >
      <DialogContent>
        <DialogCloseTrigger />
        <DialogHeader>
          <DialogTitle>API Key 삭제 확인</DialogTitle>
        </DialogHeader>
        <DialogBody>
          <Text mb={4}>
            <strong>
              {apiKey?.exchange_type} ({apiKey?.is_demo ? "모의투자" : "실전투자"})
            </strong>{" "}
            API Key를 삭제하시겠습니까?
          </Text>
          <Text color="red.500" fontSize="sm">
            이 작업은 되돌릴 수 없습니다.
          </Text>
        </DialogBody>

        <DialogFooter gap={2}>
          <ButtonGroup>
            <DialogActionTrigger asChild>
              <Button variant="subtle" colorPalette="gray" onClick={onClose}>
                취소
              </Button>
            </DialogActionTrigger>
            <Button variant="solid" colorPalette="red" onClick={onConfirm}>
              삭제
            </Button>
          </ButtonGroup>
        </DialogFooter>
      </DialogContent>
    </DialogRoot>
  )
}

export default DeleteApiKeyConfirmation
