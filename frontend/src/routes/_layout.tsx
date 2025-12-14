import { Box } from "@chakra-ui/react"
import { Outlet, createFileRoute, redirect } from "@tanstack/react-router"

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
    <Box flex="1" overflowY="auto">
      <Outlet />
    </Box>
  )
}

export default Layout
