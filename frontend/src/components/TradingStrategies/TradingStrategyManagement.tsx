import {
  Badge,
  Box,
  Button,
  Card,
  Container,
  Flex,
  Grid,
  Heading,
  HStack,
  IconButton,
  Stack,
  Text,
} from "@chakra-ui/react"
import { useState } from "react"
import { FiEdit2, FiPlus, FiTrash2 } from "react-icons/fi"

import AddTradingStrategy from "./AddTradingStrategy"
import DeleteStrategyConfirmation from "./DeleteStrategyConfirmation"
import EditTradingStrategy from "./EditTradingStrategy"
import StrategySymbols from "./StrategySymbols"

// 임시 데이터 타입
interface TradingStrategy {
  id: number
  name: string
  strategy_type: string
  description: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  config: Record<string, any>
}

// 임시 Mock 데이터
const mockStrategies: TradingStrategy[] = [
  {
    id: 1,
    name: "비트코인 그리드 전략",
    strategy_type: "GRID",
    description: "BTC 그리드 매매 전략",
    is_active: true,
    created_at: "2025-01-15T10:00:00Z",
    updated_at: "2025-01-15T10:00:00Z",
    config: {
      grid_count: 10,
      price_range: [50000000, 60000000],
      investment_amount: 1000000,
    },
  },
  {
    id: 2,
    name: "이더리움 리밸런싱",
    strategy_type: "REBALANCING",
    description: "ETH 포트폴리오 리밸런싱",
    is_active: false,
    created_at: "2025-01-10T14:30:00Z",
    updated_at: "2025-01-12T09:15:00Z",
    config: {
      rebalance_interval: "daily",
      target_ratio: 0.5,
    },
  },
  {
    id: 3,
    name: "알트코인 DCA 전략",
    strategy_type: "DCA",
    description: "정기 분할 매수 전략",
    is_active: true,
    created_at: "2025-01-01T08:00:00Z",
    updated_at: "2025-01-01T08:00:00Z",
    config: {
      interval: "weekly",
      amount_per_order: 100000,
    },
  },
]

const getStrategyTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    GRID: "그리드",
    REBALANCING: "리밸런싱",
    DCA: "적립식 매수",
  }
  return labels[type] || type
}

const getStrategyTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    GRID: "blue",
    REBALANCING: "purple",
    DCA: "green",
  }
  return colors[type] || "gray"
}

const TradingStrategyManagement = () => {
  const [strategies, setStrategies] = useState<TradingStrategy[]>(mockStrategies)
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [strategyToEdit, setStrategyToEdit] = useState<TradingStrategy | null>(
    null,
  )
  const [strategyToDelete, setStrategyToDelete] =
    useState<TradingStrategy | null>(null)
  const [selectedStrategy, setSelectedStrategy] =
    useState<TradingStrategy | null>(null)

  const handleEdit = (strategy: TradingStrategy) => {
    setStrategyToEdit(strategy)
  }

  const handleDelete = (strategy: TradingStrategy) => {
    setStrategyToDelete(strategy)
  }

  const confirmDelete = () => {
    if (strategyToDelete) {
      setStrategies(strategies.filter((s) => s.id !== strategyToDelete.id))
      setStrategyToDelete(null)
    }
  }

  const handleToggleActive = (strategyId: number) => {
    setStrategies(
      strategies.map((s) =>
        s.id === strategyId ? { ...s, is_active: !s.is_active } : s,
      ),
    )
  }

  const isLoading = false

  if (isLoading) {
    return <Text>로딩 중...</Text>
  }

  return (
    <Container maxW="full" p={0}>
      <Flex justify="space-between" align="center" mb={6}>
        <Heading size="md">등록된 매매 전략</Heading>
        <Button
          onClick={() => setIsAddModalOpen(true)}
          variant="solid"
          size="sm"
        >
          <FiPlus /> 전략 추가
        </Button>
      </Flex>

      {!strategies || strategies.length === 0 ? (
        <Box
          p={8}
          borderWidth="1px"
          borderRadius="md"
          textAlign="center"
          color="gray.500"
        >
          <Text>등록된 매매 전략이 없습니다.</Text>
          <Text fontSize="sm" mt={2}>
            상단의 "전략 추가" 버튼을 클릭하여 매매 전략을 등록하세요.
          </Text>
        </Box>
      ) : (
        <Grid
          templateColumns={{
            base: "1fr",
            md: "repeat(2, 1fr)",
            lg: "repeat(3, 1fr)",
          }}
          gap={6}
        >
          {strategies.map((strategy) => (
            <Card.Root key={strategy.id} size="sm">
              <Card.Header>
                <Flex justify="space-between" align="start">
                  <Box flex="1">
                    <Heading size="sm" mb={2}>
                      {strategy.name}
                    </Heading>
                    <HStack gap={2}>
                      <Badge
                        colorPalette={getStrategyTypeColor(
                          strategy.strategy_type,
                        )}
                        size="sm"
                      >
                        {getStrategyTypeLabel(strategy.strategy_type)}
                      </Badge>
                      <Badge
                        colorPalette={strategy.is_active ? "green" : "gray"}
                        size="sm"
                      >
                        {strategy.is_active ? "활성" : "비활성"}
                      </Badge>
                    </HStack>
                  </Box>
                  <HStack gap={1}>
                    <IconButton
                      onClick={() => handleEdit(strategy)}
                      variant="ghost"
                      size="sm"
                      aria-label="전략 수정"
                    >
                      <FiEdit2 />
                    </IconButton>
                    <IconButton
                      onClick={() => handleDelete(strategy)}
                      variant="ghost"
                      colorPalette="red"
                      size="sm"
                      aria-label="전략 삭제"
                    >
                      <FiTrash2 />
                    </IconButton>
                  </HStack>
                </Flex>
              </Card.Header>

              <Card.Body>
                <Stack gap={3}>
                  {strategy.description && (
                    <Text fontSize="sm" color="gray.600">
                      {strategy.description}
                    </Text>
                  )}

                  <Box>
                    <Text fontSize="xs" color="gray.500" mb={1}>
                      전략 설정
                    </Text>
                    <Box
                      bg="gray.50"
                      p={2}
                      borderRadius="md"
                      fontSize="xs"
                      fontFamily="mono"
                    >
                      <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>
                        {JSON.stringify(strategy.config, null, 2)}
                      </pre>
                    </Box>
                  </Box>

                  <Box>
                    <Text fontSize="xs" color="gray.500">
                      생성일:{" "}
                      {new Date(strategy.created_at).toLocaleDateString(
                        "ko-KR",
                      )}
                    </Text>
                  </Box>
                </Stack>
              </Card.Body>

              <Card.Footer>
                <Stack width="full" gap={2}>
                  <Button
                    onClick={() => handleToggleActive(strategy.id)}
                    variant="outline"
                    size="sm"
                    width="full"
                    colorPalette={strategy.is_active ? "gray" : "green"}
                  >
                    {strategy.is_active ? "비활성화" : "활성화"}
                  </Button>
                  <Button
                    onClick={() => setSelectedStrategy(strategy)}
                    variant="subtle"
                    size="sm"
                    width="full"
                  >
                    종목 관리
                  </Button>
                </Stack>
              </Card.Footer>
            </Card.Root>
          ))}
        </Grid>
      )}

      <AddTradingStrategy
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
      />

      {strategyToEdit && (
        <EditTradingStrategy
          isOpen={!!strategyToEdit}
          onClose={() => setStrategyToEdit(null)}
          strategy={strategyToEdit}
        />
      )}

      <DeleteStrategyConfirmation
        isOpen={!!strategyToDelete}
        onClose={() => setStrategyToDelete(null)}
        onConfirm={confirmDelete}
        strategy={strategyToDelete}
      />

      {selectedStrategy && (
        <StrategySymbols
          isOpen={!!selectedStrategy}
          onClose={() => setSelectedStrategy(null)}
          strategy={selectedStrategy}
        />
      )}
    </Container>
  )
}

export default TradingStrategyManagement
