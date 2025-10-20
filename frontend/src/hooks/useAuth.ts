import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import Cookies from "js-cookie"
import { useState } from "react"

import {
  type Body_login_login_access_token as AccessToken,
  type ApiError,
  LoginService,
  type UserPublic,
  type UserRegister,
  UsersService,
} from "@/client"
import { handleError } from "@/utils"

const isLoggedIn = () => {
  return Cookies.get("access_token") !== undefined
}

const useAuth = () => {
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { data: user } = useQuery<UserPublic | null, Error>({
    queryKey: ["currentUser"],
    queryFn: UsersService.readUserMe,
    enabled: isLoggedIn(),
    retry: false,
  })

  const signUpMutation = useMutation({
    mutationFn: (data: UserRegister) =>
      UsersService.registerUser({ requestBody: data }),

    onSuccess: () => {
      navigate({ to: "/login" })
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] })
    },
  })

  const login = async (data: AccessToken) => {
    const response = await LoginService.loginAccessToken({
      formData: data,
    })
    Cookies.set("access_token", response.access_token)
  }

  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: async () => {
      // 로그인 후 사용자 정보를 즉시 가져오기
      try {
        const userData = await UsersService.readUserMe()
        queryClient.setQueryData(["currentUser"], userData)
      } catch (error) {
        console.error("Failed to fetch user data after login:", error)
      }
      navigate({ to: "/" })
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
  })

  const logout = () => {
    Cookies.remove("access_token")
    queryClient.removeQueries({ queryKey: ["currentUser"] })
    window.location.reload()
  }

  return {
    signUpMutation,
    loginMutation,
    logout,
    user,
    error,
    resetError: () => setError(null),
  }
}

export { isLoggedIn }
export default useAuth
