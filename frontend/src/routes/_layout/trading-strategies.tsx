import { Container, Heading } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"

import TradingStrategyManagement from "@/components/TradingStrategies/TradingStrategyManagement"

export const Route = createFileRoute("/_layout/trading-strategies")({
  component: TradingStrategies,
})

function TradingStrategies() {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} py={12}>
        매매 전략 관리
      </Heading>
      <TradingStrategyManagement />
    </Container>
  )
}
