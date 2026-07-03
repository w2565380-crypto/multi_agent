import httpx
from app.config import settings

class DifyClient:
    def __init__(self):
        # 移除 URL 末尾的斜杠，防止拼接出错
        self.base_url = settings.DIFY_BASE_URL.rstrip('/')
        self.workflow_endpoint = f"{self.base_url}/workflows/run"

    async def run_workflow(self, api_key: str, inputs: dict, user_id: str = "backend_orchestrator") -> dict:
        """
        异步调用 Dify 的 Workflow 接口（阻塞模式）
        """
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": inputs,
            "response_mode": "blocking",  # 阻塞模式，等待执行完一次性返回
            "user": user_id
        }

        # 设置超时时间为 180秒（代码生成和测试过程耗时较长）
        timeout = httpx.Timeout(180.0, connect=10.0)

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(self.workflow_endpoint, headers=headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                
                # 检查 Dify 的业务状态
                data = result.get("data", {})
                if data.get("status") == "failed":
                    return {
                        "success": False,
                        "outputs": {},
                        "error": f"Dify Workflow Failed: {data.get('error')}"
                    }
                
                return {
                    "success": True,
                    "outputs": data.get("outputs", {}),
                    "conversation_id": result.get("conversation_id", ""),
                    "error": None
                }
            except httpx.HTTPStatusError as e:
                return {
                    "success": False, 
                    "outputs": {}, 
                    "error": f"HTTP Error {e.response.status_code}: {e.response.text}"
                }
            except Exception as e:
                return {
                    "success": False, 
                    "outputs": {}, 
                    "error": f"Connection Error: {str(e)}"
                }

# 实例化全局单例
dify_client = DifyClient()