import subprocess
from langchain.agents.middleware import AgentMiddleware, ModelRequest
from langchain.messages import SystemMessage

class SystemInfoMiddleware(AgentMiddleware):
    """fastfetch çıktısını sadece ilk çalıştırmada modele enjekte eden güvenli middleware."""

    def __init__(self):
        super().__init__()
        self._cached_message = None

    def before_model(self, request: ModelRequest) -> ModelRequest:
        if self._cached_message:
            return request

        try:
            result = subprocess.run(
                ["fastfetch", "--logo", "none"],
                capture_output=True,
                text=True,
                timeout=3
            )

            if result.returncode != 0 or not result.stdout.strip():
                info = "System info unavailable (fastfetch returned empty)."
            else:
                lines = result.stdout.strip().splitlines()[:15]
                info = "\n".join(lines)

            self._cached_message = SystemMessage(
                content=f"System environment summary (via fastfetch):\n{info}"
            )

            if hasattr(request, "messages"):
                msgs = getattr(request, "messages", [])
            elif isinstance(request, dict) and "messages" in request:
                msgs = request["messages"]
            else:
                msgs = []

            new_msgs = [self._cached_message] + list(msgs)

            if hasattr(request, "replace"):
                return request.replace(messages=new_msgs)
            elif isinstance(request, dict):
                request["messages"] = new_msgs
                return request
            else:
                return request

        except Exception as e:
            print(f"[SystemInfoMiddleware] Error: {e}")
            return request
