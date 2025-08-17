## Copyright (c) 2025 Radium-bit
## SPDX-License-Identifier: GPL-V3
## See LICENSE file for full terms
import json
import os
from tkinter import filedialog, messagebox

class ConfigHandler:
    """处理配置的保存和加载"""
    
    def __init__(self, main_window):
        self.main_window = main_window
    
    def save_config_to_json(self):
        """保存当前配置到JSON文件"""
        config_data = {
            "villager_name": self.main_window.villager_name.get().strip() or "CustomName",
            "profession": self.main_window.profession_var.get(),
            "trades": self.main_window.trade_manager.trades
        }
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="选择保存配置的路径"
        )
        if not file_path:
            return
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("成功", f"配置已保存到：\n{os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("保存失败", f"错误信息：{str(e)}")
    
    def load_config_from_json(self):
        import tkinter as tk
        """从JSON文件加载配置"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="选择要加载的JSON配置文件"
        )
        if not file_path:
            return
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            
            # 验证关键字段
            required_fields = ["villager_name", "profession", "trades"]
            if not all(field in config_data for field in required_fields):
                raise ValueError("JSON文件缺少关键字段（villager_name/profession/trades）")
            
            # 验证交易项结构
            for trade in config_data["trades"]:
                trade_required = ["buy_id", "buy_count", "sell_id", "sell_count", "max_uses", "trade_type"]
                if not all(field in trade for field in trade_required):
                    raise ValueError(f"交易项结构错误：{trade}")
            
            # 应用配置
            self.main_window.villager_name.delete(0, tk.END)
            self.main_window.villager_name.insert(0, config_data["villager_name"])
            
            # 处理职业
            if config_data["profession"] in self.main_window.professions:
                self.main_window.profession_var.set(config_data["profession"])
            else:
                messagebox.showwarning("职业不匹配", f"配置中的职业{config_data['profession']}不存在，使用默认盔甲匠")
                self.main_window.profession_var.set("armorer")
            
            # 加载交易项
            self.main_window.cancel_edit()
            self.main_window.trade_manager.trades = config_data["trades"]
            self.main_window.update_trade_listbox()
            
            messagebox.showinfo("成功", f"已加载配置：\n{os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("加载失败", f"错误信息：{str(e)}")
