import { Container, Heading } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"

import MyAssets from "@/components/Assets/MyAssets"

export const Route = createFileRoute("/_layout/my-assets")({
  component: MyAssetsPage,
})

function MyAssetsPage() {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} py={12}>
        내 자산
      </Heading>
      <MyAssets />
    </Container>
  )
}
