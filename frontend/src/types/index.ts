export interface ApiResponse<T = unknown> {
  success: boolean;
  code: number;
  msg: string | null;
  data: T;
}

export interface UserInfo {
  id: number;
  name: string;
  phone: string;
  createdAt: string | null;
  updatedAt: string | null;
}
