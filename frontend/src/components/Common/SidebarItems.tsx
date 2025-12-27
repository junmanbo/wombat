import { Box, Flex, Icon, Text } from "@chakra-ui/react"
import { Link as RouterLink } from "@tanstack/react-router"
import { FiKey, FiSettings, FiTrendingUp } from "react-icons/fi"

const items = [
  { icon: FiSettings, title: "사용자 설정", path: "/settings" as const },
  { icon: FiKey, title: "API Key", path: "/api-keys" as const },
  { icon: FiTrendingUp, title: "매매 전략", path: "/trading-strategies" as const },
]

interface SidebarItemsProps {
  onClose?: () => void
}

const SidebarItems = ({ onClose }: SidebarItemsProps) => {
  const listItems = items.map(({ icon, title, path }) => (
    <RouterLink key={title} to={path} onClick={onClose} style={{ textDecoration: 'none', color: 'inherit' }}>
      <Flex
        gap={4}
        px={4}
        py={2}
        _hover={{
          background: "gray.subtle",
        }}
        alignItems="center"
        fontSize="sm"
        cursor="pointer"
      >
        <Icon as={icon} alignSelf="center" />
        <Text ml={2}>{title}</Text>
      </Flex>
    </RouterLink>
  ))

  return (
    <>
      <Text fontSize="xs" px={4} py={2} fontWeight="bold">
        메뉴
      </Text>
      <Box>{listItems}</Box>
    </>
  )
}

export default SidebarItems
