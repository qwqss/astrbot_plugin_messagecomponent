from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.message_components import Image, Node, Plain

@register("smart_image_sender", "YourName", "智能图片折叠发送", "1.0.0")
class SmartImagePlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        # 设定阈值：超过 3 张图就折叠
        self.IMAGE_THRESHOLD = 3 

    # --- 核心功能封装 ---
    def make_smart_reply(self, event: AstrMessageEvent, components: list):
        """
        智能回复构造器
        :param event: 消息事件对象
        :param components: 准备发送的消息组件列表 (比如 [Image1, Image2, Plain...])
        :return: 构造好的 event.chain_result
        """
        # 1. 统计列表里的图片数量
        img_count = sum(1 for item in components if isinstance(item, Image))
        
        # 2. 判断是否超过阈值
        if img_count > self.IMAGE_THRESHOLD:
            logger.info(f"图片数量 {img_count} > {self.IMAGE_THRESHOLD}，转为合并转发模式")
            
            # 构造合并转发节点
            # 注意：合并转发里的显示名字通常建议用机器人的名字，或者“搜图助手”等
            bot_name = "图库助手" 
            bot_id = str(self.context.robot_id) if hasattr(self.context, "robot_id") else "10000"

            # 创建一个节点，包含所有原本要发的内容
            # 如果你想把每张图拆成一个独立的聊天气泡，可以在这里循环创建多个 Node
            # 这里演示：将所有内容塞进一个大长条气泡里
            node = Node(
                uin=bot_id,
                name=bot_name,
                content=components 
            )
            
            # 构造提示语（可选）
            tip = Plain(f"共找到 {img_count} 张图片，已折叠显示：")
            
            # 返回：[提示语, 合并转发节点]
            return event.chain_result([tip, node])
        
        else:
            # 3. 未超过阈值，直接发送原消息链
            logger.info(f"图片数量 {img_count}，直接发送")
            return event.chain_result(components)

    # --- 演示指令 ---
    @filter.command("sendimg")
    async def send_images_test(self, event: AstrMessageEvent, count: str = "1"):
        """
        测试指令：/sendimg [数量]
        模拟机器人生成指定数量的图片并发送
        """
        try:
            num = int(count)
        except ValueError:
            num = 1
        
        # 模拟生成图片列表
        # 这里使用网络图片作为示例，实际开发中你可以换成本地路径或 Base64
        # 为了演示，我们重复放入同一个测试图片链接
        test_url = "https://raw.githubusercontent.com/Soulter/AstrBot/main/assets/logo.png"
        
        msg_chain = []
        msg_chain.append(Plain(f"这是你要的 {num} 张图片：\n"))
        
        for i in range(num):
            msg_chain.append(Image.fromURL(test_url)) # 添加图片组件
            
        # --- 关键步骤：调用上面的智能回复方法 ---
        yield self.make_smart_reply(event, msg_chain)
