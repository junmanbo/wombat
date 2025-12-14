import { useState } from "react"
import {
  Box,
  Container,
  Heading,
  Text,
  VStack,
  HStack,
  Card,
  Table,
  Badge,
  Flex,
} from "@chakra-ui/react"

interface Asset {
  id: string
  symbol: string
  name: string
  quantity: number
  avgPrice: number
  currentPrice: number
  totalValue: number
  profitLoss: number
  profitLossRate: number
  exchange: string
}

// 임시 데이터
const MOCK_ASSETS: Asset[] = [
  {
    id: "1",
    symbol: "BTC",
    name: "비트코인",
    quantity: 0.5,
    avgPrice: 50000000,
    currentPrice: 55000000,
    totalValue: 27500000,
    profitLoss: 2500000,
    profitLossRate: 10,
    exchange: "Upbit",
  },
  {
    id: "2",
    symbol: "ETH",
    name: "이더리움",
    quantity: 5,
    avgPrice: 2500000,
    currentPrice: 2800000,
    totalValue: 14000000,
    profitLoss: 1500000,
    profitLossRate: 12,
    exchange: "Upbit",
  },
  {
    id: "3",
    symbol: "005930",
    name: "삼성전자",
    quantity: 100,
    avgPrice: 70000,
    currentPrice: 75000,
    totalValue: 7500000,
    profitLoss: 500000,
    profitLossRate: 7.14,
    exchange: "한국투자증권",
  },
  {
    id: "4",
    symbol: "XRP",
    name: "리플",
    quantity: 1000,
    avgPrice: 800,
    currentPrice: 750,
    totalValue: 750000,
    profitLoss: -50000,
    profitLossRate: -6.25,
    exchange: "Upbit",
  },
  {
    id: "5",
    symbol: "000660",
    name: "SK하이닉스",
    quantity: 50,
    avgPrice: 130000,
    currentPrice: 140000,
    totalValue: 7000000,
    profitLoss: 500000,
    profitLossRate: 7.69,
    exchange: "한국투자증권",
  },
]

export default function MyAssets() {
  const [assets] = useState<Asset[]>(MOCK_ASSETS)

  // 총 자산 계산
  const totalAssetValue = assets.reduce(
    (sum, asset) => sum + asset.totalValue,
    0
  )
  const totalProfitLoss = assets.reduce(
    (sum, asset) => sum + asset.profitLoss,
    0
  )
  const totalProfitLossRate = (totalProfitLoss / (totalAssetValue - totalProfitLoss)) * 100

  // 거래소별 자산 그룹화
  const assetsByExchange = assets.reduce((acc, asset) => {
    if (!acc[asset.exchange]) {
      acc[asset.exchange] = []
    }
    acc[asset.exchange].push(asset)
    return acc
  }, {} as Record<string, Asset[]>)

  const formatCurrency = (value: number, short: boolean = false): string => {
    const rounded = Math.round(value)
    if (short && rounded >= 10000) {
      return `${(rounded / 10000).toFixed(0)}만원`
    }
    return `${rounded.toLocaleString("ko-KR")}원`
  }

  const formatNumber = (value: number, decimals: number = 4): string => {
    return value.toLocaleString("ko-KR", {
      minimumFractionDigits: 0,
      maximumFractionDigits: decimals,
    })
  }

  const formatPercent = (value: number): string => {
    const sign = value >= 0 ? "+" : ""
    return `${sign}${value.toFixed(2)}%`
  }

  const getProfitLossColor = (value: number): string => {
    if (value > 0) return "green.500"
    if (value < 0) return "red.500"
    return "gray.500"
  }

  return (
    <Container maxW="full" p={0}>
      <VStack align="stretch" gap={6}>
        {/* 총 자산 요약 카드 */}
        <Card.Root>
          <Card.Body>
            <VStack align="stretch" gap={3}>
              <Heading size={{ base: "sm", md: "md" }}>총 자산 현황</Heading>
              <HStack justify="space-between" align="baseline">
                <Text fontSize={{ base: "xs", md: "sm" }} color="gray.600">
                  총 평가금액
                </Text>
                <Text fontSize={{ base: "lg", md: "2xl" }} fontWeight="bold">
                  {formatCurrency(totalAssetValue)}
                </Text>
              </HStack>
              <HStack justify="space-between" align="baseline">
                <Text fontSize={{ base: "xs", md: "sm" }} color="gray.600">
                  총 평가손익
                </Text>
                <VStack align="flex-end" gap={0}>
                  <Text
                    fontSize={{ base: "md", md: "xl" }}
                    fontWeight="semibold"
                    color={getProfitLossColor(totalProfitLoss)}
                  >
                    {formatCurrency(totalProfitLoss)}
                  </Text>
                  <Text
                    fontSize={{ base: "sm", md: "md" }}
                    color={getProfitLossColor(totalProfitLoss)}
                  >
                    {formatPercent(totalProfitLossRate)}
                  </Text>
                </VStack>
              </HStack>
            </VStack>
          </Card.Body>
        </Card.Root>

        {/* 거래소별 자산 목록 */}
        {Object.entries(assetsByExchange).map(([exchange, exchangeAssets]) => {
          const exchangeTotal = exchangeAssets.reduce(
            (sum, asset) => sum + asset.totalValue,
            0
          )
          const exchangeProfitLoss = exchangeAssets.reduce(
            (sum, asset) => sum + asset.profitLoss,
            0
          )

          return (
            <Box key={exchange}>
              <Flex
                justify="space-between"
                align="center"
                mb={4}
                flexDirection={{ base: "column", md: "row" }}
                gap={{ base: 2, md: 0 }}
              >
                <HStack>
                  <Heading size={{ base: "sm", md: "md" }}>{exchange}</Heading>
                  <Badge colorScheme="blue" size="sm">
                    {exchangeAssets.length}
                  </Badge>
                </HStack>
                <VStack align={{ base: "center", md: "flex-end" }} gap={0}>
                  <Text fontSize={{ base: "md", md: "lg" }} fontWeight="semibold">
                    {formatCurrency(exchangeTotal)}
                  </Text>
                  <Text
                    fontSize={{ base: "xs", md: "sm" }}
                    color={getProfitLossColor(exchangeProfitLoss)}
                  >
                    {formatCurrency(exchangeProfitLoss)}
                  </Text>
                </VStack>
              </Flex>

              {/* 데스크탑 테이블 뷰 */}
              <Box display={{ base: "none", md: "block" }}>
                <Card.Root>
                  <Card.Body p={0}>
                    <Box overflowX="auto">
                      <Table.Root size="sm" variant="line">
                        <Table.Header>
                          <Table.Row>
                            <Table.ColumnHeader textAlign="left">
                              종목
                            </Table.ColumnHeader>
                            <Table.ColumnHeader textAlign="right">
                              보유수량
                            </Table.ColumnHeader>
                            <Table.ColumnHeader textAlign="right">
                              평균매수가
                            </Table.ColumnHeader>
                            <Table.ColumnHeader textAlign="right">
                              현재가
                            </Table.ColumnHeader>
                            <Table.ColumnHeader textAlign="right">
                              평가금액
                            </Table.ColumnHeader>
                            <Table.ColumnHeader textAlign="right">
                              평가손익
                            </Table.ColumnHeader>
                            <Table.ColumnHeader textAlign="right">
                              수익률
                            </Table.ColumnHeader>
                          </Table.Row>
                        </Table.Header>
                        <Table.Body>
                          {exchangeAssets.map((asset) => (
                            <Table.Row key={asset.id}>
                              <Table.Cell>
                                <VStack align="flex-start" gap={0}>
                                  <Text fontWeight="semibold">{asset.name}</Text>
                                  <Text fontSize="xs" color="gray.500">
                                    {asset.symbol}
                                  </Text>
                                </VStack>
                              </Table.Cell>
                              <Table.Cell textAlign="right">
                                {formatNumber(asset.quantity)}
                              </Table.Cell>
                              <Table.Cell textAlign="right">
                                {formatCurrency(asset.avgPrice)}
                              </Table.Cell>
                              <Table.Cell textAlign="right">
                                {formatCurrency(asset.currentPrice)}
                              </Table.Cell>
                              <Table.Cell textAlign="right" fontWeight="semibold">
                                {formatCurrency(asset.totalValue)}
                              </Table.Cell>
                              <Table.Cell
                                textAlign="right"
                                color={getProfitLossColor(asset.profitLoss)}
                                fontWeight="semibold"
                              >
                                {formatCurrency(asset.profitLoss)}
                              </Table.Cell>
                              <Table.Cell
                                textAlign="right"
                                color={getProfitLossColor(asset.profitLoss)}
                                fontWeight="semibold"
                              >
                                {formatPercent(asset.profitLossRate)}
                              </Table.Cell>
                            </Table.Row>
                          ))}
                        </Table.Body>
                      </Table.Root>
                    </Box>
                  </Card.Body>
                </Card.Root>
              </Box>

              {/* 모바일 카드 뷰 */}
              <VStack align="stretch" gap={3} display={{ base: "flex", md: "none" }}>
                {exchangeAssets.map((asset) => (
                  <Card.Root key={asset.id} size="sm">
                    <Card.Body>
                      <VStack align="stretch" gap={2}>
                        {/* 종목명과 심볼 */}
                        <Flex justify="space-between" align="center">
                          <VStack align="flex-start" gap={0}>
                            <Text fontWeight="bold" fontSize="md">
                              {asset.name}
                            </Text>
                            <Text fontSize="xs" color="gray.500">
                              {asset.symbol}
                            </Text>
                          </VStack>
                          <Badge
                            colorScheme={asset.profitLoss >= 0 ? "green" : "red"}
                          >
                            {formatPercent(asset.profitLossRate)}
                          </Badge>
                        </Flex>

                        {/* 평가금액과 평가손익 */}
                        <HStack justify="space-between" pt={2} borderTopWidth="1px">
                          <VStack align="flex-start" gap={0}>
                            <Text fontSize="xs" color="gray.600">
                              평가금액
                            </Text>
                            <Text fontWeight="semibold" fontSize="lg">
                              {formatCurrency(asset.totalValue)}
                            </Text>
                          </VStack>
                          <VStack align="flex-end" gap={0}>
                            <Text fontSize="xs" color="gray.600">
                              평가손익
                            </Text>
                            <Text
                              fontWeight="semibold"
                              fontSize="lg"
                              color={getProfitLossColor(asset.profitLoss)}
                            >
                              {formatCurrency(asset.profitLoss)}
                            </Text>
                          </VStack>
                        </HStack>

                        {/* 상세 정보 */}
                        <VStack align="stretch" gap={1} pt={1}>
                          <HStack justify="space-between" fontSize="xs">
                            <Text color="gray.600">보유수량</Text>
                            <Text>{formatNumber(asset.quantity)}</Text>
                          </HStack>
                          <HStack justify="space-between" fontSize="xs">
                            <Text color="gray.600">평균매수가</Text>
                            <Text>{formatCurrency(asset.avgPrice, true)}</Text>
                          </HStack>
                          <HStack justify="space-between" fontSize="xs">
                            <Text color="gray.600">현재가</Text>
                            <Text>{formatCurrency(asset.currentPrice, true)}</Text>
                          </HStack>
                        </VStack>
                      </VStack>
                    </Card.Body>
                  </Card.Root>
                ))}
              </VStack>
            </Box>
          )
        })}
      </VStack>
    </Container>
  )
}
