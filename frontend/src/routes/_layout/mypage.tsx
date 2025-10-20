import {
  Box,
  Card,
  Container,
  Flex,
  Heading,
  Text,
  VStack,
} from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { FiMail, FiUser, FiCalendar, FiShield } from "react-icons/fi"

import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/mypage")({
  component: MyPage,
})

function MyPage() {
  const { user: currentUser } = useAuth()

  if (!currentUser) {
    return null
  }

  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return "N/A"
    return new Date(dateString).toLocaleDateString("ko-KR", {
      year: "numeric",
      month: "long",
      day: "numeric",
    })
  }

  return (
    <Container maxW="4xl" py={8}>
      <Heading size="2xl" textAlign="center" mb={8}>
        마이페이지
      </Heading>

      <VStack gap={6} align="stretch">
        {/* 프로필 카드 */}
        <Card.Root>
          <Card.Header>
            <Heading size="lg">프로필 정보</Heading>
          </Card.Header>
          <Card.Body>
            <VStack gap={4} align="stretch">
              <Flex align="center" gap={3}>
                <Box color="fg.muted">
                  <FiUser size={20} />
                </Box>
                <Box flex={1}>
                  <Text fontSize="sm" color="fg.muted">
                    이름
                  </Text>
                  <Text fontSize="md" fontWeight="medium">
                    {currentUser.full_name || "설정되지 않음"}
                  </Text>
                </Box>
              </Flex>

              <Flex align="center" gap={3}>
                <Box color="fg.muted">
                  <FiMail size={20} />
                </Box>
                <Box flex={1}>
                  <Text fontSize="sm" color="fg.muted">
                    이메일
                  </Text>
                  <Text fontSize="md" fontWeight="medium">
                    {currentUser.email}
                  </Text>
                </Box>
              </Flex>

              <Flex align="center" gap={3}>
                <Box color="fg.muted">
                  <FiShield size={20} />
                </Box>
                <Box flex={1}>
                  <Text fontSize="sm" color="fg.muted">
                    계정 권한
                  </Text>
                  <Text fontSize="md" fontWeight="medium">
                    {currentUser.is_superuser ? "관리자" : "일반 사용자"}
                  </Text>
                </Box>
              </Flex>
            </VStack>
          </Card.Body>
        </Card.Root>

        {/* 계정 정보 카드 */}
        <Card.Root>
          <Card.Header>
            <Heading size="lg">계정 정보</Heading>
          </Card.Header>
          <Card.Body>
            <VStack gap={4} align="stretch">
              <Flex align="center" gap={3}>
                <Box color="fg.muted">
                  <FiCalendar size={20} />
                </Box>
                <Box flex={1}>
                  <Text fontSize="sm" color="fg.muted">
                    가입일
                  </Text>
                  <Text fontSize="md" fontWeight="medium">
                    {formatDate(currentUser.created_at)}
                  </Text>
                </Box>
              </Flex>

              <Flex align="center" gap={3}>
                <Box color="fg.muted">
                  <FiCalendar size={20} />
                </Box>
                <Box flex={1}>
                  <Text fontSize="sm" color="fg.muted">
                    마지막 수정일
                  </Text>
                  <Text fontSize="md" fontWeight="medium">
                    {formatDate(currentUser.updated_at)}
                  </Text>
                </Box>
              </Flex>

              <Flex align="center" gap={3}>
                <Box color="fg.muted">
                  <FiUser size={20} />
                </Box>
                <Box flex={1}>
                  <Text fontSize="sm" color="fg.muted">
                    사용자 ID
                  </Text>
                  <Text fontSize="md" fontWeight="medium">
                    {currentUser.id}
                  </Text>
                </Box>
              </Flex>

              <Flex align="center" gap={3}>
                <Box color="fg.muted">
                  <FiShield size={20} />
                </Box>
                <Box flex={1}>
                  <Text fontSize="sm" color="fg.muted">
                    계정 활성 상태
                  </Text>
                  <Text fontSize="md" fontWeight="medium">
                    {currentUser.is_active ? "활성" : "비활성"}
                  </Text>
                </Box>
              </Flex>
            </VStack>
          </Card.Body>
        </Card.Root>
      </VStack>
    </Container>
  )
}
