import {
  Badge,
  Box,
  Button,
  Flex,
  Heading,
  IconButton,
  Input,
  Stack,
  Table,
  Text,
} from "@chakra-ui/react"
import { useState } from "react"
import { FiPlus, FiTrash2 } from "react-icons/fi"

import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
} from "@/components/ui/dialog"
import { Field } from "@/components/ui/field"

interface TradingStrategy {
  id: number
  name: string
  strategy_type: string
}

interface StrategySymbol {
  id: number
  symbol_id: number
  symbol_name: string
  allocation_ratio: number
  is_active: boolean
}

interface StrategySymbolsProps {
  isOpen: boolean
  onClose: () => void
  strategy: TradingStrategy
}

// Mock 데이터
const mockSymbols: StrategySymbol[] = [
  {
    id: 1,
    symbol_id: 101,
    symbol_name: "KRW-BTC",
    allocation_ratio: 0.5,
    is_active: true,
  },
  {
    id: 2,
    symbol_id: 102,
    symbol_name: "KRW-ETH",
    allocation_ratio: 0.3,
    is_active: true,
  },
  {
    id: 3,
    symbol_id: 103,
    symbol_name: "KRW-XRP",
    allocation_ratio: 0.2,
    is_active: false,
  },
]

const StrategySymbols = ({
  isOpen,
  onClose,
  strategy,
}: StrategySymbolsProps) => {
  const [symbols, setSymbols] = useState<StrategySymbol[]>(mockSymbols)
  const [isAddMode, setIsAddMode] = useState(false)
  const [newSymbolName, setNewSymbolName] = useState("")
  const [newAllocationRatio, setNewAllocationRatio] = useState("0.0")

  const handleAddSymbol = () => {
    if (!newSymbolName || !newAllocationRatio) return

    const ratio = parseFloat(newAllocationRatio)
    if (ratio < 0 || ratio > 1) {
      alert("비중은 0.0에서 1.0 사이의 값이어야 합니다.")
      return
    }

    // TODO: API 연동
    const newSymbol: StrategySymbol = {
      id: Math.max(...symbols.map((s) => s.id), 0) + 1,
      symbol_id: Math.floor(Math.random() * 1000),
      symbol_name: newSymbolName,
      allocation_ratio: ratio,
      is_active: true,
    }

    setSymbols([...symbols, newSymbol])
    setNewSymbolName("")
    setNewAllocationRatio("0.0")
    setIsAddMode(false)
  }

  const handleDeleteSymbol = (symbolId: number) => {
    // TODO: API 연동
    setSymbols(symbols.filter((s) => s.id !== symbolId))
  }

  const handleUpdateRatio = (symbolId: number, newRatio: string) => {
    const ratio = parseFloat(newRatio)
    if (ratio < 0 || ratio > 1) return

    // TODO: API 연동
    setSymbols(
      symbols.map((s) =>
        s.id === symbolId ? { ...s, allocation_ratio: ratio } : s,
      ),
    )
  }

  const totalRatio = symbols
    .filter((s) => s.is_active)
    .reduce((sum, s) => sum + s.allocation_ratio, 0)

  return (
    <DialogRoot open={isOpen} onOpenChange={onClose} size="xl">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>종목 관리 - {strategy.name}</DialogTitle>
        </DialogHeader>
        <DialogCloseTrigger />

        <DialogBody>
          <Stack gap={4}>
            <Flex justify="space-between" align="center">
              <Box>
                <Heading size="sm" mb={1}>
                  등록된 종목
                </Heading>
                <Text fontSize="sm" color="gray.600">
                  총 비중:{" "}
                  <Badge
                    colorPalette={
                      totalRatio === 1
                        ? "green"
                        : totalRatio > 1
                          ? "red"
                          : "yellow"
                    }
                  >
                    {(totalRatio * 100).toFixed(2)}%
                  </Badge>
                </Text>
              </Box>
              <Button
                onClick={() => setIsAddMode(!isAddMode)}
                variant="outline"
                size="sm"
              >
                <FiPlus /> 종목 추가
              </Button>
            </Flex>

            {isAddMode && (
              <Box p={4} borderWidth="1px" borderRadius="md" bg="gray.50">
                <Heading size="xs" mb={3}>
                  새 종목 추가
                </Heading>
                <Stack gap={3}>
                  <Field label="종목">
                    <Input
                      value={newSymbolName}
                      onChange={(e) => setNewSymbolName(e.target.value)}
                      placeholder="예: KRW-BTC"
                      size="sm"
                    />
                  </Field>
                  <Field label="비중 (0.0 ~ 1.0)">
                    <Input
                      type="number"
                      value={newAllocationRatio}
                      onChange={(e) => setNewAllocationRatio(e.target.value)}
                      min={0}
                      max={1}
                      step={0.1}
                      size="sm"
                    />
                  </Field>
                  <Flex gap={2}>
                    <Button onClick={handleAddSymbol} size="sm" flex="1">
                      추가
                    </Button>
                    <Button
                      onClick={() => setIsAddMode(false)}
                      variant="outline"
                      size="sm"
                      flex="1"
                    >
                      취소
                    </Button>
                  </Flex>
                </Stack>
              </Box>
            )}

            {symbols.length === 0 ? (
              <Box
                p={8}
                borderWidth="1px"
                borderRadius="md"
                textAlign="center"
                color="gray.500"
              >
                <Text>등록된 종목이 없습니다.</Text>
                <Text fontSize="sm" mt={2}>
                  "종목 추가" 버튼을 클릭하여 종목을 추가하세요.
                </Text>
              </Box>
            ) : (
              <Box overflowX="auto">
                <Table.Root size="sm" variant="outline">
                  <Table.Header>
                    <Table.Row>
                      <Table.ColumnHeader>종목</Table.ColumnHeader>
                      <Table.ColumnHeader>비중</Table.ColumnHeader>
                      <Table.ColumnHeader>상태</Table.ColumnHeader>
                      <Table.ColumnHeader>작업</Table.ColumnHeader>
                    </Table.Row>
                  </Table.Header>
                  <Table.Body>
                    {symbols.map((symbol) => (
                      <Table.Row key={symbol.id}>
                        <Table.Cell>
                          <Text fontWeight="medium">{symbol.symbol_name}</Text>
                        </Table.Cell>
                        <Table.Cell>
                          <Input
                            type="number"
                            value={symbol.allocation_ratio.toString()}
                            onChange={(e) =>
                              handleUpdateRatio(symbol.id, e.target.value)
                            }
                            min={0}
                            max={1}
                            step={0.05}
                            size="sm"
                            width="100px"
                          />
                        </Table.Cell>
                        <Table.Cell>
                          <Badge
                            colorPalette={symbol.is_active ? "green" : "gray"}
                            size="sm"
                          >
                            {symbol.is_active ? "활성" : "비활성"}
                          </Badge>
                        </Table.Cell>
                        <Table.Cell>
                          <IconButton
                            onClick={() => handleDeleteSymbol(symbol.id)}
                            variant="ghost"
                            colorPalette="red"
                            size="sm"
                            aria-label="종목 삭제"
                          >
                            <FiTrash2 />
                          </IconButton>
                        </Table.Cell>
                      </Table.Row>
                    ))}
                  </Table.Body>
                </Table.Root>
              </Box>
            )}

            {totalRatio !== 1 && symbols.length > 0 && (
              <Box p={3} bg="yellow.50" borderRadius="md">
                <Text fontSize="sm" color="yellow.800">
                  ⚠️ 전체 비중의 합이 100%가 아닙니다. 전략이 제대로 실행되지
                  않을 수 있습니다.
                </Text>
              </Box>
            )}
          </Stack>
        </DialogBody>

        <DialogFooter>
          <Button onClick={onClose} variant="outline">
            닫기
          </Button>
        </DialogFooter>
      </DialogContent>
    </DialogRoot>
  )
}

export default StrategySymbols
