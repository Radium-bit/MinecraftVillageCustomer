## Copyright (c) 2025 Radium-bit
## SPDX-License-Identifier: GPL-V3
## See LICENSE file for full terms
import re
import hashlib

class NbtHandler:
    """处理NBT标签的解析、构建和哈希计算"""
    
    def parse_item_with_nbt(self, item_input):
        """
        解析包含NBT标签的物品输入
        输入格式: namespace:item{tag1:value1,tag2:{nested:value},...}
        或: item{tag} (自动添加minecraft:前缀)
        或: item (自动添加minecraft:前缀)
        
        返回: (item_id, nbt_tags) 元组，nbt_tags为解析后的标签字符串或None
        """
        item_input = item_input.strip()
        
        # 正则表达式匹配物品ID和NBT标签
        pattern = r'^([a-zA-Z0-9_]+:)?[a-zA-Z0-9_]+(?:\{.*\})?$'
        if not re.match(pattern, item_input):
            raise ValueError(f"无效的物品格式: {item_input}\n正确格式示例: minecraft:bow 或 tacz:gun{Tag:value}")
        
        # 分离物品ID和NBT标签
        nbt_start = item_input.find('{')
        nbt_end = item_input.rfind('}')
        
        if nbt_start != -1 and nbt_end != -1 and nbt_start < nbt_end:
            item_id_part = item_input[:nbt_start]
            nbt_tags = item_input[nbt_start:nbt_end+1]
        else:
            item_id_part = item_input
            nbt_tags = None
        
        # 处理物品ID（仅当不含命名空间时添加minecraft:）
        if ':' not in item_id_part:
            item_id = f"minecraft:{item_id_part}"
        else:
            item_id = item_id_part
        
        return (item_id, nbt_tags)

    def build_item_nbt_string(self, item_input, count):
        """构建完整的物品NBT字符串"""
        try:
            item_id, nbt_tags = self.parse_item_with_nbt(item_input)
            
            # 基础NBT结构
            parts = [f'id:"{item_id}"', f'Count:{count}b']
            
            # 如果有标签，添加tag部分
            if nbt_tags:
                # 移除标签外的大括号
                inner_tags = nbt_tags[1:-1] if nbt_tags.startswith('{') and nbt_tags.endswith('}') else nbt_tags
                parts.insert(1, f'tag:{{{inner_tags}}}')
            
            return '{' + ', '.join(parts) + '}'
        except Exception as e:
            raise ValueError(f"构建物品NBT失败: {str(e)}")

    def get_nbt_hash(self, nbt_tags):
        """计算NBT标签的短哈希值（前7个字符）"""
        if not nbt_tags:
            return None
        
        # 使用MD5哈希算法
        hash_obj = hashlib.md5(nbt_tags.encode('utf-8'))
        # 返回前7个十六进制字符
        return hash_obj.hexdigest()[:7]

    def simplify_item_id(self, item_id):
        """简化物品ID显示（移除命名空间和标签）"""
        simplified = re.sub(r'{.*$', '', item_id)
        return simplified.replace("minecraft:", "")
