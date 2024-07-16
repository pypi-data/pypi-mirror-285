import json
from urllib.parse import unquote
from agent.fegin.portal_client import PortalClient


class MemoryService:
    def __init__(self, logger, portal_address, system_config):
        self.logger = logger
        self.portal_client = PortalClient(logger, portal_address, system_config)

    # 检查当前轮对话是否上传pdf文档
    def check_last_contain_pdf(self, data):
        second_last_element = data[-2]
        if 'resourceList' in second_last_element:
            resource_list = second_last_element['resourceList']
            if resource_list:
                for item in resource_list:
                    if '.pdf' in item.lower():
                        return True
        return False

    # 获取history中最后一个pdf文档的index
    def find_last_pdf_order_index(self, data):
        # 查找包含 PDF 类型的最后一个文档的 orderIndex
        last_pdf_order_index = None
        for message in reversed(data):
            if 'resourceList' in message and message['resourceList']:
                for resource in message['resourceList']:
                    if '.pdf' in resource.lower():
                        last_pdf_order_index = message['orderIndex']
                        break
            if last_pdf_order_index:
                break
        return last_pdf_order_index

    # 获取完整的memory信息，包括所使用的工具
    def retrieve_complete_memory(self, session_id: str, max_round: int = 20, max_length: int = 4000):
        self.logger.info(f'根据session_id[%s]从portal后端查询retrieve_complete_memory', session_id)
        memories = []
        try:
            memory_resp = self.portal_client.get_chat_detail(session_id)
            if memory_resp is None or memory_resp.get("data") is None or memory_resp.get("data").get("conversation") is None:
                self.logger.info(f'根据session_id[%s]从portal后端查询历史消息为空，请检查参数', session_id)
                self.logger.info(f'retrieve_memory,session_id[{session_id}],return[]')
                return []
            chat_info_list = memory_resp.get('data').get('conversation')
            if len(chat_info_list) < 2:
                self.logger.info(f"retrieve_complete_memory,len(chat_info_list) < 2, return[],session_id={session_id}")
                self.logger.info(f'retrieve_complete_memory,session_id[{session_id}],return[]')
                return []
            chat_info_list = chat_info_list[:-2]
            memory_length = 0
            memory_round = 0
            for i in range(len(chat_info_list) - 1, -1, -2):
                chat_memory = {}
                if chat_info_list[i - 1]['text'] is not None and chat_info_list[i]['text'] is not None:
                    chat = chat_info_list[i - 1]["text"]
                    chat = chat.replace("\\n", "\n")
                    chat_memory.update({"question": chat, "chatId": chat_info_list[i - 1]["chatId"]})
                    files = []
                    if len(chat_info_list[i - 1]["resourceList"]) > 0:
                        for resource in chat_info_list[i - 1]["resourceList"]:
                            data = json.loads(resource)
                            files.append(data['url'])
                    chat_memory.update({'files': files})
                    content = self.retrieve_content_from_answer(chat_info_list[i]['text'])
                    content = content.replace("\\n", "\n")
                    plugin = chat_info_list[i]["pluginCode"]
                    chat_memory.update({"answer": content})
                    chat_memory.update({"plugin": plugin})
                    memories.insert(0, chat_memory)
                memory_round = memory_round + 1
                if chat_memory is not None:
                    memory_length = memory_length + len(chat_memory)
                if max_round > 0 and memory_round >= max_round:
                    self.logger.info(f'当前历史对话轮数超过{max_round}轮,不再新增历史对话,session_id[{session_id}]')
                    break
                if max_length > 0 and memory_length >= max_length:
                    self.logger.info(f'当前历史对话字符长度超过{max_length},不再新增历史对话,session_id[{session_id}]')
                    break
        except Exception as e:
            self.logger.error("获取历史消息时，发生%s异常", str(e), exc_info=True)
        self.logger.info(f'retrieve_complete_memory,session_id[{session_id}],return[{memories}]')
        return memories

    def retrieve_memory(self, session_id: str, split_pdf: bool = False):
        self.logger.info(f'根据session_id[%s]从portal后端查询历史消息, split_pdf=[%s]', session_id, split_pdf)
        memories = []
        try:
            memory_resp = self.portal_client.get_chat_detail(session_id)
            if memory_resp is None or memory_resp.get("data") is None or memory_resp.get("data").get("conversation") is None:
                self.logger.info(f'根据session_id[%s]从portal后端查询历史消息为空，请检查参数', session_id)
                self.logger.info(f'retrieve_memory,session_id[{session_id}],return[]')
                return []
            chat_info_list = memory_resp.get('data').get('conversation')
            if len(chat_info_list) < 2:
                self.logger.info(f"retrieve_memory,len(chat_info_list) < 2, return[],session_id={session_id}")
                self.logger.info(f'retrieve_memory,session_id[{session_id}],return[]')
                return []
            # 如果本轮对话上传了pdf，则不传history
            if self.check_last_contain_pdf(chat_info_list):
                self.logger.info(f"chat contain pdf, return[],session_id={session_id}")
                self.logger.info(f'retrieve_memory,session_id[{session_id}],return[]')
                return []
            chat_info_list = chat_info_list[:-2]
            if split_pdf:
                # 对于文献解析，本轮没有上传pdf，则需要清除上一个pdf之前的history
                last_pdf_index = self.find_last_pdf_order_index(chat_info_list)
                if last_pdf_index is not None:
                    chat_info_list = chat_info_list[last_pdf_index:]
            num = 0
            memory_length = 0
            for i in range(0, len(chat_info_list), 2):
                chat_memory = []
                if chat_info_list[i]['text'] is not None and chat_info_list[i + 1]['text'] is not None:
                    chat = chat_info_list[i]["text"]
                    chat = chat.replace("\\n", "\n")
                    chat_memory.append(chat)
                    content = self.retrieve_content_from_answer(chat_info_list[i + 1]['text'])
                    content = content.replace("\\n", "\n")
                    chat_memory.append(content)
                    memories.append(chat_memory)
                num += 1
                if chat_memory is not None:
                    memory_length = memory_length + len(chat_memory)
                if num >= 20:
                    self.logger.info(f'当前历史对话轮数超过20轮,不再新增历史对话,session_id[{session_id}]')
                    break
                if memory_length >= 4000:
                    self.logger.info(f'当前历史对话字符长度超过4000,不再新增历史对话,session_id[{session_id}]')
                    break
        except Exception as e:
            self.logger.error("获取历史消息时，发生%s异常", str(e), exc_info=True)
        self.logger.info(f'retrieve_memory,session_id[{session_id}],return[{memories}]')
        return memories

    def retrieve_content_from_answer(self, content):
        '''处理历史消息中各式各样的markdown格式和json格式'''
        self.logger.info(f"retrieve_content_from_answer data:[{content}]")
        all_contents = ''
        try:
            data = json.loads(content)
            # 遍历列表，提取每个元素的content字段，并进行URL解码
            for item in data:
                content = unquote(item['content'])
                if 'MarkDown' == unquote(item['type']) or 'MarkDownTable' == unquote(item['type']):
                    all_contents += content  # 添加换行符以区分不同内容
        except Exception as e:
            self.logger.error("加载历史消息时，发生%s异常", str(e), exc_info=True)
        return all_contents
