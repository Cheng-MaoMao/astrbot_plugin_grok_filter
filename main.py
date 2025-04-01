import re
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.provider import LLMResponse


@register("grok-filter", "Cheng-MaoMao", "可选择是否过滤推理模型的思考内容", "1.0.0",
          'https://github.com/Cheng-MaoMao/astrbot_plugin_grok_filter')
class R1Filter(Star):
    """
    过滤大模型思考内容的插件

    此插件主要用于过滤grok-3-reasoner模型的思考内容，使用户能够选择是否显示模型在生成回复前的思考过程。
    思考内容通常被包含在<think></think>标签中。
    """

    def __init__(self, context: Context, config: dict):
        """
        初始化过滤器

        参数:
            context: 星河机器人上下文对象
            config: 插件配置字典，包含display_reasoning_text等配置项
        """
        super().__init__(context)
        self.config = config
        # 从配置中获取是否显示思考内容的设置，默认为不显示(False)
        self.display_reasoning_text = self.config.get('display_reasoning_text', False)

    @filter.on_llm_response()
    async def resp(self, event: AstrMessageEvent, response: LLMResponse):
        """
        响应处理器，过滤LLM回复中的思考内容

        参数:
            event: 消息事件对象
            response: 大语言模型的响应对象
        """
        # 如果用户设置了不显示思考内容
        if not self.display_reasoning_text:
            completion_text = response.completion_text

            # 适配 grok-3-reasoner 模型的思考内容过滤
            if r'<think>' in completion_text and r'</think>' in completion_text:
                # 使用正则表达式查找并移除<think></think>标签中的所有内容
                # flags=re.DOTALL 确保可以匹配跨越多行的内容
                # count=1 表示只替换第一次出现的匹配项
                # strip()用于移除可能产生的多余空白
                completion_text = re.sub(r'<think>.*?</think>', '', completion_text, count=1,
                                         flags=re.DOTALL).strip()

                # 开发调试信息
                # print(f"已过滤grok-3-reasoner的思考内容，过滤后长度: {len(completion_text)}")

            # 更新响应文本，替换为过滤后的内容
            response.completion_text = completion_text