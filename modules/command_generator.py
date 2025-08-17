## Copyright (c) 2025 Radium-bit
## SPDX-License-Identifier: GPL-V3
## See LICENSE file for full terms
class CommandGenerator:
    """生成Minecraft指令的核心类"""
    
    def generate_all_commands(self, villager_name, profession, trades, nbt_handler):
        """生成所有步骤的指令"""
        custom_name_nbt = f'{{"text":"{villager_name}"}}'
        
        # 设置CustomName
        cmd_step0 = (
            f'/data modify entity @e[type=villager,name="{villager_name}",limit=1]  CustomName set value {custom_name_nbt}'
        )
        
        # 设置VillagerData
        cmd_step1 = (
            f'/data modify entity @e[type=villager,name="{villager_name}",limit=1]  VillagerData set value '
            f'{{profession:{profession},level:5}}'
        )
        
        # 设置PersistenceRequired
        cmd_step2 = (
            f'/data modify entity @e[type=villager,name="{villager_name}",limit=1]  PersistenceRequired set value 1b'
        )
        
        # 设置CustomNameVisible
        cmd_step3 = (
            f'/data modify entity @e[type=villager,name="{villager_name}",limit=1]  CustomNameVisible set value 1b'
        )
        
        # 设置Offers.Recipes（交易列表）
        cmd_step4 = self.generate_trade_command(villager_name, trades, nbt_handler)
        
        return [cmd_step0, cmd_step1, cmd_step2, cmd_step3, cmd_step4]
    
    def generate_trade_command(self, villager_name, trades, nbt_handler):
        """生成交易列表指令"""
        recipes = []
        for trade in trades:
            try:
                # 构建buy和sell的NBT
                buy_nbt = nbt_handler.build_item_nbt_string(trade["buy_id"], trade["buy_count"])
                sell_nbt = nbt_handler.build_item_nbt_string(trade["sell_id"], trade["sell_count"])
                
                recipes.append(
                    f'{{buy:{buy_nbt},sell:{sell_nbt},maxUses:{trade["max_uses"]}}}'
                )
            except Exception as e:
                raise ValueError(f"生成交易项失败 {trade['buy_id']} → {trade['sell_id']}: {str(e)}")
        
        recipes_str = ",\n    ".join(recipes)
        return (
            f'/data modify entity @e[type=villager,name="{villager_name}",limit=1] Offers.Recipes set value '
            f'[{recipes_str}]'
        )
