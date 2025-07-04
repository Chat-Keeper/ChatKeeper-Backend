# app/services/chat_parser.py
import re
from typing import List, Dict
from datetime import datetime


class ChatLogParser:
    """聊天记录解析器（适配QQ导出格式）"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        # 匹配格式: 2024-04-21 1:35:26 2362269434(2362269434)
        self.header_pattern = re.compile(
            r'^(\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2}) (.+?)(?:\((\d+)\)|<([^>]+)>)$'
        )

    def parse_messages(self) -> List[Dict]:
        """解析QQ导出的聊天记录文件"""
        messages = []
        current_header = None
        content_lines = []
        header_found = False  # 标记是否找到第一个有效消息头

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()

                    # 跳过文件头信息
                    if not header_found:
                        if "消息对象:" in line:
                            header_found = True
                        continue

                    # 跳过分隔线
                    if line.startswith("=" * 64):
                        continue

                    # 检查是否为消息头
                    header_match = self.header_pattern.match(line)
                    if header_match:
                        # 保存上一条消息
                        if current_header and content_lines:
                            time_str, speaker_name, speaker_id = current_header
                            content = '\n'.join(content_lines)
                            messages.append(self._format_message(
                                time_str, speaker_name, speaker_id, content
                            ))
                            content_lines = []

                        # 解析新消息头
                        time_str = header_match.group(1)
                        speaker_name = header_match.group(2)
                        qq_id = header_match.group(3)
                        email = header_match.group(4)
                        if qq_id:
                            current_header = (time_str, speaker_name, qq_id)
                        else:
                            if email:
                                current_header = (time_str, speaker_name, email)
                    elif current_header:
                        # 添加到当前消息内容
                        content_lines.append(line)

            # 添加最后一条消息
            if current_header and content_lines:
                time_str, speaker_name, speaker_id = current_header
                content = '\n'.join(content_lines)
                messages.append(self._format_message(
                    time_str, speaker_name, speaker_id, content
                ))

            return messages

        except UnicodeDecodeError:
            # 尝试使用其他编码
            try:
                return self._parse_with_backup_encodings()
            except Exception:
                raise ValueError("无法解码文件，请使用UTF-8格式")
        except Exception as e:
            raise RuntimeError(f"解析聊天记录失败: {str(e)}")

    def _format_message(self, time_str: str, speaker_name: str,
                        speaker_id: str, content: str) -> Dict:
        """格式化消息为字典"""
        return {
            'time_str': time_str.strip(),
            'speaker_name': speaker_name.strip(),
            'speaker_id': speaker_id.strip(),
            'content': content.strip()
        }

    def _parse_time(self, time_str: str) -> str:
        """解析QQ消息时间格式"""
        try:
            # QQ时间格式: "2024-04-21 1:35:26"
            if len(time_str.split(':')[0].split()[-1]) == 1:
                time_str = time_str.replace(' ', ' 0', 1)
            return datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return time_str  # 返回原始字符串如果解析失败

    def _parse_with_backup_encodings(self) -> List[Dict]:
        """使用备用编码尝试解析"""
        encodings = ['gbk', 'latin-1', 'utf-16']
        for encoding in encodings:
            try:
                with open(self.file_path, 'r', encoding=encoding) as f:
                    content = f.read()

                # 保存为UTF-8后重新解析
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                return self.parse_messages()
            except:
                continue

        raise UnicodeDecodeError("无法确定文件编码")