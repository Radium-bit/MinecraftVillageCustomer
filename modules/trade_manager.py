## Copyright (c) 2025 Radium-bit
## SPDX-License-Identifier: GPL-V3
## See LICENSE file for full terms
class TradeManager:
    """管理交易项的核心类，负责交易项的添加、修改、删除等操作"""
    
    def __init__(self):
        self.trades = []
    
    def init_default_trades(self):
        """初始化默认交易项"""
        self.trades = [
            {
                "buy_id": "minecraft:emerald", 
                "buy_count": "1", 
                "buy2_id": "minecraft:air",
                "buy2_count": "1",
                "sell_id": "minecraft:grass_block", 
                "sell_count": "1", 
                "max_uses": "256",
                "trade_type": "emerald_buy"
            }
        ]
    
    def add_trade(self, trade):
        """添加新交易项"""
        self.trades.append(trade)
    
    def add_trades(self, trades):
        """批量添加交易项"""
        self.trades.extend(trades)
    
    def update_trade(self, index, trade):
        """更新指定索引的交易项"""
        if 0 <= index < len(self.trades):
            self.trades[index] = trade
    
    def delete_trades(self, indices):
        """删除指定索引的交易项"""
        # 逆序删除避免索引偏移
        for idx in sorted(indices, reverse=True):
            if 0 <= idx < len(self.trades):
                del self.trades[idx]
    
    def swap_trades(self, index1, index2):
        """交换两个交易项的位置"""
        if 0 <= index1 < len(self.trades) and 0 <= index2 < len(self.trades):
            self.trades[index1], self.trades[index2] = self.trades[index2], self.trades[index1]
    
    def reverse_trades(self):
        """反转交易项（考虑村民只能输出一种物品，调整反转逻辑）"""
        reversed_trades = []
        for trade in self.trades:
            reversed_trade = {
                # 原输出物品变为新的输入物品
                "buy_id": trade["sell_id"],
                "buy_count": trade["sell_count"],
                # 原第一个输入物品变为新的输出物品（丢弃原第二个输入物品）
                "sell_id": trade["buy_id"],
                "sell_count": trade["buy_count"],
                "max_uses": trade["max_uses"],
                # 切换交易类型
                "trade_type": "item_sell" if trade["trade_type"] == "emerald_buy" else "emerald_buy"
            }
            reversed_trades.append(reversed_trade)
        return reversed_trades
