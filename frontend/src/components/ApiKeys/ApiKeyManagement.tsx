import {
  Box,
  Button,
  Container,
  Flex,
  Heading,
  Table,
  Text,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { FiPlus, FiTrash2 } from "react-icons/fi"

import {
  type ApiError,
  type UserApiKeyPublic,
  UserApiKeysService,
} from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

import AddApiKey from "./AddApiKey"
import DeleteApiKeyConfirmation from "./DeleteApiKeyConfirmation"

const ApiKeyManagement = () => {
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [apiKeyToDelete, setApiKeyToDelete] = useState<UserApiKeyPublic | null>(
    null,
  )

  const { data: apiKeys, isLoading } = useQuery({
    queryKey: ["apiKeys"],
    queryFn: () => UserApiKeysService.readUserApiKeys({}),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) =>
      UserApiKeysService.deleteUserApiKey({ apiKeyId: id }),
    onSuccess: () => {
      showSuccessToast("API Key가 성공적으로 삭제되었습니다.")
      queryClient.invalidateQueries({ queryKey: ["apiKeys"] })
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
  })

  const handleDelete = (apiKey: UserApiKeyPublic) => {
    setApiKeyToDelete(apiKey)
  }

  const confirmDelete = () => {
    if (apiKeyToDelete) {
      deleteMutation.mutate(apiKeyToDelete.id)
      setApiKeyToDelete(null)
    }
  }

  if (isLoading) {
    return <Text>로딩 중...</Text>
  }

  return (
    <Container maxW="full">
      <Flex justify="space-between" align="center" mb={6}>
        <Heading size="md">등록된 API Key</Heading>
        <Button
          onClick={() => setIsAddModalOpen(true)}
          variant="solid"
          size="sm"
        >
          <FiPlus /> API Key 추가
        </Button>
      </Flex>

      {!apiKeys?.data || apiKeys.data.length === 0 ? (
        <Box
          p={8}
          borderWidth="1px"
          borderRadius="md"
          textAlign="center"
          color="gray.500"
        >
          <Text>등록된 API Key가 없습니다.</Text>
          <Text fontSize="sm" mt={2}>
            상단의 "API Key 추가" 버튼을 클릭하여 거래소 API Key를 등록하세요.
          </Text>
        </Box>
      ) : (
        <Box overflowX="auto">
          <Table.Root size="sm" variant="outline">
            <Table.Header>
              <Table.Row>
                <Table.ColumnHeader>거래소</Table.ColumnHeader>
                <Table.ColumnHeader>계좌번호</Table.ColumnHeader>
                <Table.ColumnHeader>별칭</Table.ColumnHeader>
                <Table.ColumnHeader>타입</Table.ColumnHeader>
                <Table.ColumnHeader>상태</Table.ColumnHeader>
                <Table.ColumnHeader>생성일</Table.ColumnHeader>
                <Table.ColumnHeader>작업</Table.ColumnHeader>
              </Table.Row>
            </Table.Header>
            <Table.Body>
              {apiKeys.data.map((apiKey) => (
                <Table.Row key={apiKey.id}>
                  <Table.Cell>
                    <Text fontWeight="medium">{apiKey.exchange_type}</Text>
                  </Table.Cell>
                  <Table.Cell>
                    <Text>{apiKey.account_number || "-"}</Text>
                  </Table.Cell>
                  <Table.Cell>
                    <Text>{apiKey.nickname || "-"}</Text>
                  </Table.Cell>
                  <Table.Cell>
                    <Text>{apiKey.is_demo ? "모의투자" : "실전투자"}</Text>
                  </Table.Cell>
                  <Table.Cell>
                    <Text color={apiKey.is_active ? "green.500" : "red.500"}>
                      {apiKey.is_active ? "활성" : "비활성"}
                    </Text>
                  </Table.Cell>
                  <Table.Cell>
                    <Text fontSize="sm">
                      {new Date(apiKey.created_at).toLocaleDateString("ko-KR")}
                    </Text>
                  </Table.Cell>
                  <Table.Cell>
                    <Button
                      onClick={() => handleDelete(apiKey)}
                      variant="ghost"
                      colorPalette="red"
                      size="sm"
                    >
                      <FiTrash2 />
                    </Button>
                  </Table.Cell>
                </Table.Row>
              ))}
            </Table.Body>
          </Table.Root>
        </Box>
      )}

      <AddApiKey
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
      />

      <DeleteApiKeyConfirmation
        isOpen={!!apiKeyToDelete}
        onClose={() => setApiKeyToDelete(null)}
        onConfirm={confirmDelete}
        apiKey={apiKeyToDelete}
      />
    </Container>
  )
}

export default ApiKeyManagement
