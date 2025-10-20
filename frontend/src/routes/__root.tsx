import { Flex } from "@chakra-ui/react"
import { Outlet, createRootRoute } from "@tanstack/react-router"
import React, { Suspense } from "react"

import Navbar from "@/components/Common/Navbar"
import NotFound from "@/components/Common/NotFound"

const loadDevtools = () =>
  Promise.all([
    import("@tanstack/router-devtools"),
    import("@tanstack/react-query-devtools"),
  ]).then(([routerDevtools, reactQueryDevtools]) => {
    return {
      default: () => (
        <>
          <routerDevtools.TanStackRouterDevtools />
          <reactQueryDevtools.ReactQueryDevtools />
        </>
      ),
    }
  })

const TanStackDevtools =
  process.env.NODE_ENV === "production" ? () => null : React.lazy(loadDevtools)

export const Route = createRootRoute({
  component: () => (
    <Flex direction="column" h="100vh">
      <Navbar />
      <Flex flex="1" direction="column" overflowY="auto">
        <Outlet />
      </Flex>
      <Suspense>
        <TanStackDevtools />
      </Suspense>
    </Flex>
  ),
  notFoundComponent: () => <NotFound />,
})
