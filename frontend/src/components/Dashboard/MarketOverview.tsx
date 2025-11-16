import { useEffect, useState } from "react"
import {
  Box,
  Container,
  Heading,
  Spinner,
  Text,
  VStack,
  HStack,
  Card,
} from "@chakra-ui/react"
import { SymbolsService, PriceDataService } from "@/client"
import type { SymbolPublic, PriceDataPublic } from "@/client"

interface MarketItemData {
  symbol: SymbolPublic
  priceData: PriceDataPublic | null
  displayName: string
}

// 표시할 코인 목록 (base_asset 기준)
const CRYPTO_ASSETS = ["BTC", "ETH", "USDT", "XRP", "SOL"]

// 표시할 주식 목록 (symbol 코드 기준)
const STOCK_SYMBOLS = [
  { code: "005930", name: "삼성전자" },
  { code: "000660", name: "SK하이닉스" },
  { code: "373220", name: "LG에너지솔루션" },
  { code: "207940", name: "삼성바이오로직스" },
  { code: "005380", name: "현대차" },
]

export default function MarketOverview() {
  const [cryptoData, setCryptoData] = useState<MarketItemData[]>([])
  const [stockData, setStockData] = useState<MarketItemData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchMarketData()
  }, [])

  const fetchMarketData = async () => {
    try {
      setLoading(true)
      setError(null)

      // 모든 심볼 가져오기
      const symbolsResponse = await SymbolsService.readSymbols({ limit: 1000 })
      const allSymbols = symbolsResponse.data

      // 코인 데이터 필터링 및 가져오기
      const cryptoSymbols = allSymbols.filter(
        (s) =>
          s.symbol_type === "CRYPTO" &&
          s.base_asset &&
          CRYPTO_ASSETS.includes(s.base_asset)
      )

      // 주식 데이터 필터링 및 가져오기
      const stockSymbols = allSymbols.filter(
        (s) =>
          s.symbol_type === "STOCK" &&
          STOCK_SYMBOLS.some((stock) => stock.code === s.symbol)
      )

      // 디버깅: 모든 주식 종목 확인
      console.log("=== 디버깅: 전체 주식 종목 ===")
      const allStocks = allSymbols.filter((s) => s.symbol_type === "STOCK")
      console.log(`전체 주식 종목 수: ${allStocks.length}`)
      allStocks.forEach((s) => {
        console.log(`종목코드: ${s.symbol}, 종목명: ${s.base_asset}`)
      })

      console.log("\n=== 찾으려는 종목들 ===")
      STOCK_SYMBOLS.forEach((stock) => {
        const found = allSymbols.find((s) => s.symbol === stock.code)
        console.log(`${stock.name} (${stock.code}): ${found ? '발견됨' : '없음'}`)
      })

      console.log(`\n필터링된 주식 종목 수: ${stockSymbols.length}`)

      // 코인 가격 데이터 가져오기
      const cryptoWithPrices = await Promise.all(
        cryptoSymbols.map(async (symbol) => {
          try {
            const priceData = await PriceDataService.readLatestPriceData({
              symbolId: symbol.id,
              timeframe: "1d",
            })

            return {
              symbol,
              priceData,
              displayName: symbol.base_asset || symbol.symbol,
            }
          } catch (err) {
            console.error(
              `Failed to fetch price for ${symbol.symbol}:`,
              err
            )
            return {
              symbol,
              priceData: null,
              displayName: symbol.base_asset || symbol.symbol,
            }
          }
        })
      )

      // 주식 가격 데이터 가져오기
      const stockWithPrices = await Promise.all(
        stockSymbols.map(async (symbol) => {
          try {
            const priceData = await PriceDataService.readLatestPriceData({
              symbolId: symbol.id,
              timeframe: "1d",
            })

            const stockInfo = STOCK_SYMBOLS.find((s) => s.code === symbol.symbol)
            return {
              symbol,
              priceData,
              displayName: stockInfo?.name || symbol.base_asset || symbol.symbol,
            }
          } catch (err) {
            console.error(
              `Failed to fetch price for ${symbol.symbol}:`,
              err
            )
            const stockInfo = STOCK_SYMBOLS.find((s) => s.code === symbol.symbol)
            return {
              symbol,
              priceData: null,
              displayName: stockInfo?.name || symbol.base_asset || symbol.symbol,
            }
          }
        })
      )

      setCryptoData(cryptoWithPrices)
      setStockData(stockWithPrices)
    } catch (err) {
      console.error("Failed to fetch market data:", err)
      setError("시장 데이터를 불러오는데 실패했습니다.")
    } finally {
      setLoading(false)
    }
  }

  const formatPrice = (price: string): string => {
    const num = parseFloat(price)
    return `${Math.round(num).toLocaleString('ko-KR')} 원`
  }

  const formatVolume = (volume: string): string => {
    const num = parseFloat(volume)
    if (num >= 1000000000) {
      return `${(num / 1000000000).toFixed(2)}B`
    } else if (num >= 1000000) {
      return `${(num / 1000000).toFixed(2)}M`
    } else if (num >= 1000) {
      return `${(num / 1000).toFixed(2)}K`
    }
    return num.toLocaleString()
  }

  const MarketCard = ({ item }: { item: MarketItemData }) => (
    <Card.Root>
      <Card.Body>
        <VStack align="stretch" gap={2}>
          <HStack justify="space-between">
            <Text fontWeight="bold" fontSize="lg">
              {item.displayName}
            </Text>
            <Text fontSize="sm" color="gray.500">
              {item.symbol.symbol}
            </Text>
          </HStack>

          {item.priceData ? (
            <>
              <HStack justify="space-between">
                <Text fontSize="sm" color="gray.600">
                  종가
                </Text>
                <Text fontWeight="semibold" fontSize="md">
                  {formatPrice(item.priceData.close_price)}
                </Text>
              </HStack>

              <HStack justify="space-between">
                <Text fontSize="sm" color="gray.600">
                  거래량
                </Text>
                <Text fontSize="sm">{formatVolume(item.priceData.volume)}</Text>
              </HStack>

              <Text fontSize="xs" color="gray.400">
                {new Date(item.priceData.timestamp).toLocaleDateString()}
              </Text>
            </>
          ) : (
            <Text fontSize="sm" color="gray.500">
              가격 데이터 없음
            </Text>
          )}
        </VStack>
      </Card.Body>
    </Card.Root>
  )

  if (loading) {
    return (
      <Container maxW="full">
        <Box pt={8} textAlign="center">
          <Spinner size="xl" />
          <Text mt={4}>시장 데이터 로딩 중...</Text>
        </Box>
      </Container>
    )
  }

  if (error) {
    return (
      <Container maxW="full">
        <Box pt={8}>
          <Text color="red.500">{error}</Text>
        </Box>
      </Container>
    )
  }

  return (
    <Container maxW="full">
      <VStack align="stretch" gap={6} pt={6}>
        {/* 코인 섹션 */}
        <Box>
          <Heading size="lg" mb={4}>
            암호화폐
          </Heading>
          {cryptoData.length > 0 ? (
            <HStack gap={4} overflowX="auto" pb={2}>
              {cryptoData.map((item) => (
                <Box key={item.symbol.id} minW="250px">
                  <MarketCard item={item} />
                </Box>
              ))}
            </HStack>
          ) : (
            <Text color="gray.500">코인 데이터가 없습니다.</Text>
          )}
        </Box>

        {/* 주식 섹션 */}
        <Box>
          <Heading size="lg" mb={4}>
            국내 주식
          </Heading>
          {stockData.length > 0 ? (
            <HStack gap={4} overflowX="auto" pb={2}>
              {stockData.map((item) => (
                <Box key={item.symbol.id} minW="250px">
                  <MarketCard item={item} />
                </Box>
              ))}
            </HStack>
          ) : (
            <Text color="gray.500">주식 데이터가 없습니다.</Text>
          )}
        </Box>
      </VStack>
    </Container>
  )
}
