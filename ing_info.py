import time
import requests
from bridge.reply import Reply, ReplyType
from config import conf
from common.log import logger
import plugins
from plugins import Plugin, Event, EventContext, EventAction


def create_channel_object():
    # 从配置中获取频道类型
    channel_type = conf().get("channel_type")
    # 根据频道类型创建相应的频道对象
    if channel_type == 'wework':
        from channel.wework.wework_channel import WeworkChannel
        return WeworkChannel(), ReplyType.IMAGE_URL, 2
    if channel_type == 'wx':
        from channel.wechat.wechat_channel import WechatChannel
        return WechatChannel(), ReplyType.IMAGE, 2
    elif channel_type == "wechatcom_app":
        from channel.wechatcom.wechatcomapp_channel import WechatComAppChannel
        return WechatComAppChannel(), ReplyType.IMAGE_URL, 2
    else:
        from channel.wechat.wechat_channel import WechatChannel
        return WechatChannel(), ReplyType.IMAGE_URL, 2


@plugins.register(
    name="img_info",
    desire_priority=94,
    hidden=True,
    desc="A plugin that drawing",
    version="0.1",
    author="lanvent",
)
class Drawing(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info("[Drawing] inited")
        self.comapp, self.type, self.num = create_channel_object()

    def on_handle_context(self, e_context: EventContext):
        content = e_context["context"].content
        if content.startswith("画"):
            self.text_to_image(e_context, content[len("画"):])

    def text_to_image(self, e_context, query):
        self.send_task_submission_message(e_context, query)

        image_url = "xxx"
        # print(response.data[0].url)
        reply = Reply()
        reply.type = ReplyType.IMAGE_URL
        reply.content = image_url
        e_context["reply"] = reply
        e_context.action = EventAction.BREAK_PASS

    def get_help_text(self, **kwargs):
        help_text = (
            "💡输入 '画 <绘画内容与风格描述>'，我会帮您实现图片生成\n"
        )
        return help_text

    def send_task_submission_message(self, e_context, task_message):
        com_reply = Reply()
        com_reply.type = ReplyType.TEXT
        context = e_context['context']
        msg = context.kwargs.get('msg')
        nickname = msg.actual_user_nickname
        com_reply.content = "@{name}\n☑️任务创建成功！\n🆔任务内容：{task}\n⏳努力绘画中，预计耗时1分钟，请您耐心等待...".format(
            name=nickname, task=task_message)
        self.comapp.send(com_reply, context)
