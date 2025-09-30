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
import { Link as RouterLink } from "@tanstack/react-router"

export const Route = createFileRoute("/")({
  component: Index,
})

function Index() {
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
            <Text>My Assets</Text>
          </RouterLink>
          <RouterLink to="/">
            <Text>Trading Strategies</Text>
          </RouterLink>
          <RouterLink to="/">
            <Text>Backtesting</Text>
          </RouterLink>
        </HStack>

        <HStack>
          <RouterLink to="/login">
            <Button colorScheme="teal" variant="ghost">
              Login
            </Button>
          </RouterLink>
          <RouterLink to="/signup">
            <Button colorScheme="teal" variant="solid">
              Sign Up
            </Button>
          </RouterLink>
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
          Automate Your Trading,
          <br />
          <Text as={"span"} color={"teal.400"}>
            Maximize Your Profits
          </Text>
        </Heading>
        <Text color={"gray.500"}>
          Join Wombat Invest and unlock the power of automated stock and crypto
          trading.
          <br />
          Create, test, and deploy your trading strategies with ease.
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
              Get Started
            </Button>
          </RouterLink>
        </Stack>
      </Stack>
    </Container>
  )
}
