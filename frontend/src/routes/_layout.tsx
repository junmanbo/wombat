import { Flex } from "@chakra-ui/react"
import { Outlet, createFileRoute, redirect } from "@tanstack/react-router"

import Sidebar from "@/components/Common/Sidebar"
import { isLoggedIn } from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout")({
  component: Layout,
  beforeLoad: async ({ location }) => {
    if (!isLoggedIn() && location.pathname !== "/") {
      throw redirect({
        to: "/login",
      })
    }
  },
})

function Layout() {
  return (
    <Flex flex="1" overflow="hidden">
      <Sidebar />
      <Flex flex="1" direction="column" p={4} overflowY="auto">
        <Outlet />
      </Flex>
    </Flex>
  )
}

export default Layout
