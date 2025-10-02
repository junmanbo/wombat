import {
  Box,
  Button,
  Container,
  Flex,
  Heading,
  HStack,
  Stack,
  Text,
} from "@chakra-ui/react"
import { createFileRoute, Link as RouterLink } from "@tanstack/react-router"

import useAuth, { isLoggedIn } from "@/hooks/useAuth"

export const Route = createFileRoute("/")({
  component: Index,
})

function Index() {
  const { logout } = useAuth()
  const loggedIn = isLoggedIn()

  return (
    <Container maxW="container.xl" p={0}>
      <Flex as="nav" align="center" justify="space-between" wrap="wrap" p={6}>
        <Flex align="center" mr={5}>
          <Heading as="h1" size="lg" letterSpacing={"tighter"}>
            Wombat Invest
          </Heading>
        </Flex>

        <HStack
          spacing={8}
          alignItems={"center"}
          display={{ base: "none", md: "flex" }}
        >
          <RouterLink to="/">
            <Text>내 자산</Text>
          </RouterLink>
          <RouterLink to="/">
            <Text>매매 전략</Text>
          </RouterLink>
          <RouterLink to="/">
            <Text>백테스팅</Text>
          </RouterLink>
        </HStack>

        <HStack>
          {loggedIn ? (
            <Button colorScheme="teal" variant="ghost" onClick={logout}>
              로그아웃
            </Button>
          ) : (
            <>
              <RouterLink to="/login">
                <Button colorScheme="teal" variant="ghost">
                  로그인
                </Button>
              </RouterLink>
              <RouterLink to="/signup">
                <Button colorScheme="teal" variant="solid">
                  가입하기
                </Button>
              </RouterLink>
            </>
          )}
        </HStack>
      </Flex>

      <Stack
        as={Box}
        textAlign={"center"}
        spacing={{ base: 8, md: 14 }}
        py={{ base: 20, md: 36 }}
      >
        <Heading
          fontWeight={600}
          fontSize={{ base: "2xl", sm: "4xl", md: "6xl" }}
          lineHeight={"110%"}
        >
          거래를 자동화하고,
          <br />
          <Text as={"span"} color={"teal.400"}>
            수익을 극대화하세요
          </Text>
        </Heading>
        <Text color={"gray.500"}>
          Wombat Invest에 가입하여 자동화된 주식 및 암호화폐 거래의 힘을 활용하십시오.
          <br />
          거래 전략을 쉽게 생성, 테스트 및 배포하십시오.
        </Text>
        <Stack
          direction={"column"}
          spacing={3}
          align={"center"}
          alignSelf={"center"}
          position={"relative"}
        >
          <RouterLink to="/signup">
            <Button
              colorScheme={"teal"}
              bg={"teal.400"}
              rounded={"full"}
              px={6}
              _hover={{
                bg: "teal.500",
              }}
            >
              시작하기
            </Button>
          </RouterLink>
        </Stack>
      </Stack>
    </Container>
  )
}
