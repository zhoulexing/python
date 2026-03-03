import request from "./request";
import type { ApiResponse, UserInfo } from "@/types";

export function getMockUser() {
  return request.get<unknown, ApiResponse<UserInfo>>("/example/user/mock");
}
