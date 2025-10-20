import {
  Button,
  Flex,
  Heading,
  HStack,
  Text,
} from "@chakra-ui/react"
import { Link as RouterLink } from "@tanstack/react-router"

import { isLoggedIn } from "@/hooks/useAuth"
import UserMenu from "./UserMenu"

function Navbar() {
  const loggedIn = isLoggedIn()

  return (
    <Flex
      as="nav"
      align="center"
      justify="space-between"
      wrap="wrap"
      p={6}
      position="sticky"
      top={0}
      bg="bg"
      zIndex={10}
      borderBottomWidth="1px"
      borderColor="border"
    >
      <Flex align="center" mr={5}>
        <RouterLink to="/">
          <Heading as="h1" size="lg" letterSpacing={"tighter"}>
            Wombat Invest
          </Heading>
        </RouterLink>
      </Flex>

      <HStack
        gap={8}
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
          <UserMenu />
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
  )
}

export default Navbar
