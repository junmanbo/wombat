import { Button, ButtonGroup, Text } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { useForm } from "react-hook-form"

import { type ApiError, UsersService } from "@/client"
import {
  DialogActionTrigger,
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const DeleteConfirmation = () => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    handleSubmit,
    formState: { isSubmitting },
  } = useForm()
  const { logout } = useAuth()

  const mutation = useMutation({
    mutationFn: () => UsersService.deleteUserMe(),
    onSuccess: () => {
      showSuccessToast("계정이 성공적으로 삭제되었습니다")
      setIsOpen(false)
      logout()
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["currentUser"] })
    },
  })

  const onSubmit = async () => {
    mutation.mutate()
  }

  return (
    <>
      <DialogRoot
        size={{ base: "xs", md: "md" }}
        role="alertdialog"
        placement="center"
        open={isOpen}
        onOpenChange={({ open }) => setIsOpen(open)}
      >
        <DialogTrigger asChild>
          <Button variant="solid" colorPalette="red" mt={4}>
            삭제
          </Button>
        </DialogTrigger>

        <DialogContent>
          <form onSubmit={handleSubmit(onSubmit)}>
            <DialogCloseTrigger />
            <DialogHeader>
              <DialogTitle>확인 필요</DialogTitle>
            </DialogHeader>
            <DialogBody>
              <Text mb={4}>
                모든 계정 데이터가 <strong>영구적으로 삭제됩니다.</strong> 계속하시려면{" "}
                <strong>"확인"</strong> 버튼을 클릭하세요. 이 작업은 되돌릴 수 없습니다.
              </Text>
            </DialogBody>

            <DialogFooter gap={2}>
              <ButtonGroup>
                <DialogActionTrigger asChild>
                  <Button
                    variant="subtle"
                    colorPalette="gray"
                    disabled={isSubmitting}
                  >
                    취소
                  </Button>
                </DialogActionTrigger>
                <Button
                  variant="solid"
                  colorPalette="red"
                  type="submit"
                  loading={isSubmitting}
                >
                  확인
                </Button>
              </ButtonGroup>
            </DialogFooter>
          </form>
        </DialogContent>
      </DialogRoot>
    </>
  )
}

export default DeleteConfirmation
