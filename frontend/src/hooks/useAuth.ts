import { useMutateApi } from "./useCallApi";
import type {
  ReqUserLogin,
  ReqUserRegister,
  ResUserToken,
  UserLoginData,
} from "@/models/auth";
import type { ResponseWrapper } from "@/models/globalTypes";

export const useLogin = () => {
  const {
    mutateAsync: loginMutation,
    isPending: isLoginPending,
    error: loginError,
  } = useMutateApi<ResponseWrapper<UserLoginData>, ReqUserLogin>();

  const login = async (data: ReqUserLogin) => {
    return loginMutation({
      url: "/auth/login",
      method: "POST",
      data,
    });
  };

  return {
    login,
    isLoginPending,
    loginError,
  };
};

export const useRegister = () => {
  const {
    mutateAsync: registerMutation,
    isPending: isRegisterPending,
    error: registerError,
  } = useMutateApi<ResponseWrapper<UserLoginData>, ReqUserRegister>();

  const register = async (data: ReqUserRegister) => {
    return registerMutation({
      url: "/auth/register",
      method: "POST",
      data,
    });
  };

  return {
    register,
    isRegisterPending,
    registerError,
  };
};

export const useRefreshToken = () => {
  const {
    mutateAsync: refreshTokenMutation,
    isPending: isRefreshTokenPending,
    error: refreshTokenError,
  } = useMutateApi<ResponseWrapper<ResUserToken>>();

  const refreshToken = async () => {
    return refreshTokenMutation({
      url: "/auth/refresh-token",
      method: "GET",
    });
  };

  return {
    refreshToken,
    isRefreshTokenPending,
    refreshTokenError,
  };
};
