import { useEffect, useState } from "react";
import { getMockUser } from "@/api/example";
import type { UserInfo } from "@/types";

export default function HomePage() {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchUser = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getMockUser();
      if (res.success) {
        setUser(res.data);
      } else {
        setError(res.msg ?? "请求失败");
      }
    } catch (e: any) {
      setError(e.message ?? "网络错误");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUser();
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-medium text-gray-800">Mock 用户接口测试</h2>
        <button
          onClick={fetchUser}
          disabled={loading}
          className="rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "加载中..." : "刷新"}
        </button>
      </div>

      {error && (
        <div className="rounded bg-red-50 p-4 text-sm text-red-600">{error}</div>
      )}

      {user && (
        <div className="rounded-lg bg-white p-6 shadow">
          <dl className="grid grid-cols-2 gap-x-8 gap-y-4 text-sm">
            <div>
              <dt className="text-gray-500">ID</dt>
              <dd className="mt-1 font-medium text-gray-900">{user.id}</dd>
            </div>
            <div>
              <dt className="text-gray-500">姓名</dt>
              <dd className="mt-1 font-medium text-gray-900">{user.name}</dd>
            </div>
            <div>
              <dt className="text-gray-500">手机号</dt>
              <dd className="mt-1 font-medium text-gray-900">{user.phone}</dd>
            </div>
            <div>
              <dt className="text-gray-500">创建时间</dt>
              <dd className="mt-1 font-medium text-gray-900">{user.createdAt ?? "-"}</dd>
            </div>
          </dl>
        </div>
      )}
    </div>
  );
}
