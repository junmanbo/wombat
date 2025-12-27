import { Container, Heading } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"

import ApiKeyManagement from "@/components/ApiKeys/ApiKeyManagement"

export const Route = createFileRoute("/_layout/api-keys")({
  component: ApiKeys,
})

function ApiKeys() {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} py={12}>
        API Key 관리
      </Heading>
      <ApiKeyManagement />
    </Container>
  )
}
