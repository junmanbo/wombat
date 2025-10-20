import { Container, Heading, Text } from "@chakra-ui/react"

import DeleteConfirmation from "./DeleteConfirmation"

const DeleteAccount = () => {
  return (
    <Container maxW="full">
      <Heading size="sm" py={4}>
        계정 삭제
      </Heading>
      <Text>
        계정과 관련된 모든 데이터를 영구적으로 삭제합니다.
      </Text>
      <DeleteConfirmation />
    </Container>
  )
}
export default DeleteAccount
