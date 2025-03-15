import re
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.provider import LLMResponse
from openai.types.chat.chat_completion import ChatCompletion


@register("qwq-filter", "beat4ocean", "可选择是否过滤推理模型的思考内容", "1.0.3",
          'https://github.com/beat4ocean/astrbot_plugin_qwq_filter')
class R1Filter(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config
        self.display_reasoning_text = self.config.get('display_reasoning_text', False)

    @filter.on_llm_response()
    async def resp(self, event: AstrMessageEvent, response: LLMResponse):
        if not self.display_reasoning_text:
            completion_text = response.completion_text
            # 适配 qwq 模型
            if r'</details>' in completion_text:
                if r'<details style=' in completion_text:
                    # 过滤带有 style 的 <details> 标签及内容
                    completion_text = re.sub(r'<details style=".*?" open>.*?</details>', '', completion_text, count=1,
                                             flags=re.DOTALL).strip()
                elif r'<details>' in completion_text:
                    # 过滤普通的 <details> 标签及内容
                    completion_text = re.sub(r'<details>.*?</details>', '', completion_text, count=1,
                                             flags=re.DOTALL).strip()
                elif r'<details' not in completion_text:
                    # 只过滤第一个 </details> 及之前的内容
                    completion_text = re.sub(r'.*?</details>', '', completion_text, count=1, flags=re.DOTALL).strip()
            response.completion_text = completion_text
