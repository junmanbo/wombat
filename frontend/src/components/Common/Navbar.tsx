import {
  Button,
  Flex,
  Heading,
  HStack,
  IconButton,
  Text,
  Box,
} from "@chakra-ui/react"
import { Link as RouterLink } from "@tanstack/react-router"
import { useState } from "react"
import { FiMenu, FiX } from "react-icons/fi"

import useAuth from "@/hooks/useAuth"
import UserMenu from "./UserMenu"

function Navbar() {
  const { user } = useAuth()
  const loggedIn = !!user
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen)
  }

  return (
    <Box
      as="nav"
      position="sticky"
      top={0}
      bg="bg"
      zIndex={100}
      borderBottomWidth="1px"
      borderColor="border"
    >
      <Flex
        align="center"
        justify="space-between"
        px={{ base: 4, md: 6 }}
        py={4}
      >
        {/* 로고 */}
        <Flex align="center">
          <RouterLink to="/">
            <Heading as="h1" size={{ base: "md", md: "lg" }} letterSpacing={"tighter"}>
              웜뱃
            </Heading>
          </RouterLink>
        </Flex>

        {/* 데스크탑 메뉴 */}
        <HStack
          gap={8}
          alignItems={"center"}
          display={{ base: "none", md: "flex" }}
        >
          <RouterLink to="/my-assets">
            <Text
              _hover={{ color: "teal.500" }}
              transition="color 0.2s"
            >
              내 자산
            </Text>
          </RouterLink>
          <RouterLink to="/trading-strategies">
            <Text
              _hover={{ color: "teal.500" }}
              transition="color 0.2s"
            >
              매매 전략
            </Text>
          </RouterLink>
          <RouterLink to="/">
            <Text
              _hover={{ color: "teal.500" }}
              transition="color 0.2s"
            >
              백테스팅
            </Text>
          </RouterLink>
        </HStack>

        {/* 우측 메뉴 */}
        <HStack gap={2}>
          {loggedIn ? (
            <>
              <UserMenu />
              {/* 모바일 메뉴 버튼 */}
              <IconButton
                aria-label="Toggle menu"
                onClick={toggleMobileMenu}
                display={{ base: "flex", md: "none" }}
                variant="ghost"
              >
                {mobileMenuOpen ? <FiX /> : <FiMenu />}
              </IconButton>
            </>
          ) : (
            <>
              <RouterLink to="/login">
                <Button colorScheme="teal" variant="ghost" size={{ base: "sm", md: "md" }}>
                  로그인
                </Button>
              </RouterLink>
              <RouterLink to="/signup">
                <Button colorScheme="teal" variant="solid" size={{ base: "sm", md: "md" }}>
                  가입하기
                </Button>
              </RouterLink>
            </>
          )}
        </HStack>
      </Flex>

      {/* 모바일 메뉴 드롭다운 */}
      {mobileMenuOpen && loggedIn && (
        <Box
          display={{ base: "block", md: "none" }}
          pb={4}
          px={4}
          borderTopWidth="1px"
          borderColor="border"
        >
          <Flex direction="column" gap={3}>
            <RouterLink to="/my-assets" onClick={toggleMobileMenu}>
              <Text
                py={2}
                px={3}
                borderRadius="md"
                _hover={{ bg: "gray.100" }}
                transition="background 0.2s"
              >
                내 자산
              </Text>
            </RouterLink>
            <RouterLink to="/trading-strategies" onClick={toggleMobileMenu}>
              <Text
                py={2}
                px={3}
                borderRadius="md"
                _hover={{ bg: "gray.100" }}
                transition="background 0.2s"
              >
                매매 전략
              </Text>
            </RouterLink>
            <RouterLink to="/" onClick={toggleMobileMenu}>
              <Text
                py={2}
                px={3}
                borderRadius="md"
                _hover={{ bg: "gray.100" }}
                transition="background 0.2s"
              >
                백테스팅
              </Text>
            </RouterLink>
          </Flex>
        </Box>
      )}
    </Box>
  )
}

export default Navbar
