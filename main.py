## Copyright (c) 2025 Radium-bit
## SPDX-License-Identifier: GPL-V3
## See LICENSE file for full terms
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os

class VillagerTradeGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft村民交易指令生成器 v0.1 by.Radiumbit")
        self.root.geometry("900x900")
        
        # 存储交易项的列表：每个元素为字典{buy_id, buy_count, sell_id, sell_count, max_uses, trade_type}
        self.trades = []
        # 定义列表行的灰度背景（偶数行浅灰，奇数行深灰）
        self.row_grays = ["#f0f0f0", "#e0e0e0"]
        # 存储当前选中的待修改交易项索引
        self.selected_edit_idx = None
        
        # ---------------------- 顶部功能按钮栏----------------------
        self.top_btn_frame = ttk.Frame(root)
        self.top_btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.save_btn = ttk.Button(self.top_btn_frame, text="保存配置到JSON", command=self.save_config_to_json)
        self.save_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.load_btn = ttk.Button(self.top_btn_frame, text="加载JSON预设", command=self.load_config_from_json)
        self.load_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # ---------------------- 村民基础信息区域 ----------------------
        self.villager_frame = ttk.LabelFrame(root, text="村民基础信息")
        self.villager_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 村民名称
        ttk.Label(self.villager_frame, text="村民名称:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.villager_name = ttk.Entry(self.villager_frame, width=30)
        self.villager_name.grid(row=0, column=1, padx=5, pady=5, columnspan=2)
        self.villager_name.insert(0, "CustomName")
        
        # 职业选择
        ttk.Label(self.villager_frame, text="职业:").grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        self.professions = [
            "armorer", "butcher", "cartographer", "cleric", "farmer", "fisherman",
            "fletcher", "leatherworker", "librarian", "mason", "shepherd",
            "toolsmith", "weaponsmith"
        ]
        self.profession_var = tk.StringVar()
        self.profession_combo = ttk.Combobox(
            self.villager_frame, textvariable=self.profession_var, values=self.professions, state="readonly"
        )
        self.profession_combo.grid(row=0, column=4, padx=5, pady=5)
        self.profession_combo.current(0)
        
        # ---------------------- 交易项编辑区域 ----------------------
        self.trade_edit_frame = ttk.LabelFrame(root, text="交易项编辑（单次交易/右键列表项修改）")
        self.trade_edit_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 交易类型（单选）
        self.trade_type_var = tk.StringVar(value="emerald_buy")
        ttk.Radiobutton(
            self.trade_edit_frame, text="绿宝石买物品（buy=绿宝石, sell=目标物品）", 
            variable=self.trade_type_var, value="emerald_buy",
            command=self.swap_buy_sell_on_trade_type_switch
        ).grid(row=0, column=0, padx=5, pady=5, columnspan=3, sticky=tk.W)
        ttk.Radiobutton(
            self.trade_edit_frame, text="物品换绿宝石（buy=目标物品, sell=绿宝石）", 
            variable=self.trade_type_var, value="item_sell",
            command=self.swap_buy_sell_on_trade_type_switch
        ).grid(row=1, column=0, padx=5, pady=5, columnspan=3, sticky=tk.W)
        
        # Buy方物品
        ttk.Label(self.trade_edit_frame, text="Buy方物品ID:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.buy_id = ttk.Entry(self.trade_edit_frame, width=20)
        self.buy_id.grid(row=2, column=1, padx=5, pady=5)
        self.buy_id.insert(0, "minecraft:emerald")
        
        ttk.Label(self.trade_edit_frame, text="数量:").grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)
        self.buy_count = ttk.Entry(self.trade_edit_frame, width=10)
        self.buy_count.grid(row=2, column=3, padx=5, pady=5)
        self.buy_count.insert(0, "1")
        
        # Sell方物品
        ttk.Label(self.trade_edit_frame, text="Sell方物品ID:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.sell_id = ttk.Entry(self.trade_edit_frame, width=20)
        self.sell_id.grid(row=3, column=1, padx=5, pady=5)
        self.sell_id.insert(0, "minecraft:grass_block")
        
        ttk.Label(self.trade_edit_frame, text="数量:").grid(row=3, column=2, padx=5, pady=5, sticky=tk.W)
        self.sell_count = ttk.Entry(self.trade_edit_frame, width=10)
        self.sell_count.grid(row=3, column=3, padx=5, pady=5)
        self.sell_count.insert(0, "1")
        
        # 最大交易次数
        ttk.Label(self.trade_edit_frame, text="最大交易次数(maxUses):").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.max_uses = ttk.Entry(self.trade_edit_frame, width=10)
        self.max_uses.grid(row=4, column=1, padx=5, pady=5)
        self.max_uses.insert(0, "256")
        
        # 添加/修改按钮
        self.add_modify_btn = ttk.Button(self.trade_edit_frame, text="添加交易项", command=self.add_or_modify_trade)
        self.add_modify_btn.grid(row=4, column=2, padx=5, pady=5)
        
        # 取消修改按钮
        self.cancel_edit_btn = ttk.Button(self.trade_edit_frame, text="取消修改", command=self.cancel_edit)
        self.cancel_edit_btn.grid(row=4, column=3, padx=5, pady=5)
        self.cancel_edit_btn.grid_remove()  # 初始隐藏
        
        # ---------------------- 交易项列表区域 ----------------------
        self.trade_list_frame = ttk.LabelFrame(root, text="已添加的交易项（右键列表项可修改参数）")
        self.trade_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 列表操作按钮栏
        self.list_btn_frame = ttk.Frame(self.trade_list_frame)
        self.list_btn_frame.pack(fill=tk.X, padx=5, pady=3)
        
        self.reverse_btn = ttk.Button(self.list_btn_frame, text="一键反转追加交易", command=self.reverse_append_trades)
        self.reverse_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.move_up_btn = ttk.Button(self.list_btn_frame, text="上移选中项", command=self.move_trade_up)
        self.move_up_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.move_down_btn = ttk.Button(self.list_btn_frame, text="下移选中项", command=self.move_trade_down)
        self.move_down_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.del_btn = ttk.Button(self.list_btn_frame, text="删除选中交易（支持多选）", command=self.delete_trade)
        self.del_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # 列表框（支持多选+右键菜单）
        ttk.Label(self.list_btn_frame, text="交易项预览：buy[ID:数量] → sell[ID:数量] | maxUses").pack(side=tk.LEFT, padx=10, pady=2)
        self.trade_listbox = tk.Listbox(
            self.trade_list_frame, width=110, height=12, selectbackground="#4a86e8", 
            selectforeground="white", selectmode=tk.EXTENDED
        )
        self.trade_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        # 绑定右键菜单事件
        self.trade_listbox.bind("<Button-3>", self.show_trade_right_click_menu)
        
        # 初始化右键菜单
        self.trade_right_menu = tk.Menu(self.root, tearoff=0)
        self.trade_right_menu.add_command(label="修改此交易项", command=self.start_edit_selected_trade)
        
        # 初始化默认交易项
        self.init_default_trades()
        
        # ---------------------- 指令生成区域 ----------------------
        self.result_frame = ttk.LabelFrame(root, text="生成的指令")
        self.result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.gen_btn = ttk.Button(self.result_frame, text="生成指令", command=self.generate_command)
        self.gen_btn.pack(anchor=tk.W, padx=5, pady=5)
        
        self.command_text = tk.Text(self.result_frame, wrap=tk.WORD, width=110, height=12)
        self.command_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.command_text.config(state=tk.DISABLED)

    def init_default_trades(self):
        """初始化默认交易项（绿宝石换草方块）"""
        default_trades = [
            {
                "buy_id": "minecraft:emerald", 
                "buy_count": "1", 
                "sell_id": "minecraft:grass_block", 
                "sell_count": "1", 
                "max_uses": "256",
                "trade_type": "emerald_buy"
            }
        ]
        self.trades = default_trades
        self.update_trade_listbox()

    def update_trade_listbox(self):
        """更新交易项列表框（隔行灰度+交易类型颜色）"""
        self.trade_listbox.delete(0, tk.END)
        for idx, trade in enumerate(self.trades):
            # 简化物品ID显示
            buy_id_simple = trade["buy_id"].replace("minecraft:", "")
            sell_id_simple = trade["sell_id"].replace("minecraft:", "")
            buy_info = f"{buy_id_simple}:{trade['buy_count']}"
            sell_info = f"{sell_id_simple}:{trade['sell_count']}"
            item_text = f"{idx+1}. buy[{buy_info}] → sell[{sell_info}] | maxUses:{trade['max_uses']}"
            
            # 设置背景色（隔行灰度+交易类型色）
            if trade["trade_type"] == "emerald_buy":
                final_bg = "#e8f8e8" if idx % 2 == 0 else "#d8e8d8"
            else:
                final_bg = "#f8e8f8" if idx % 2 == 0 else "#e8d8e8"
            
            # 插入列表项
            self.trade_listbox.insert(tk.END, item_text)
            self.trade_listbox.itemconfig(idx, bg=final_bg)

    def swap_buy_sell_on_trade_type_switch(self):
        """切换交易类型时，自动互换Buy和Sell方的ID与数量"""
        # 1. 保存当前Buy/Sell输入框的内容
        current_buy_id = self.buy_id.get().strip()
        current_buy_count = self.buy_count.get().strip()
        current_sell_id = self.sell_id.get().strip()
        current_sell_count = self.sell_count.get().strip()

        # 2. 根据切换后的交易类型，决定是否互换内容
        target_trade_type = self.trade_type_var.get()
        if target_trade_type == "emerald_buy":
            # 切换到“绿宝石买物品”：Buy方强制为绿宝石，Sell方保留原Buy方内容
            new_buy_id = "minecraft:emerald"
            new_buy_count = current_buy_count  # 数量沿用原Buy方
            new_sell_id = current_buy_id if current_buy_id != "minecraft:emerald" else current_sell_id
            new_sell_count = current_buy_count if current_buy_id != "minecraft:emerald" else current_sell_count
        else:
            # 切换到“物品换绿宝石”：Buy方用原Sell方内容，Sell方强制为绿宝石
            new_buy_id = current_sell_id
            new_buy_count = current_sell_count
            new_sell_id = "minecraft:emerald"
            new_sell_count = current_buy_count  # 数量沿用原Buy方

        # 3. 清空输入框并填充互换后的内容（保留默认值逻辑）
        self.buy_id.delete(0, tk.END)
        self.buy_id.insert(0, new_buy_id if new_buy_id else "minecraft:emerald")
        
        self.buy_count.delete(0, tk.END)
        self.buy_count.insert(0, new_buy_count if new_buy_count.isdigit() else "1")
        
        self.sell_id.delete(0, tk.END)
        self.sell_id.insert(0, new_sell_id if new_sell_id else "minecraft:grass_block")
        
        self.sell_count.delete(0, tk.END)
        self.sell_count.insert(0, new_sell_count if new_sell_count.isdigit() else "1")


    # ---------------------- 右键修改功能相关 ----------------------
    def show_trade_right_click_menu(self, event):
        """显示右键菜单（仅当右键选中单个列表项时）"""
        # 获取右键点击位置对应的列表项索引
        click_idx = self.trade_listbox.nearest(event.y)
        # 检查该索引是否在有效范围内且未被选中，若未选中则选中
        if 0 <= click_idx < len(self.trades) and click_idx not in self.trade_listbox.curselection():
            self.trade_listbox.selection_clear(0, tk.END)
            self.trade_listbox.selection_set(click_idx)
        
        # 仅当选中单个项时显示右键菜单
        selected_idx = self.trade_listbox.curselection()
        if len(selected_idx) == 1:
            self.trade_right_menu.post(event.x_root, event.y_root)

    def start_edit_selected_trade(self):
        """开始修改选中的交易项（右键菜单触发）"""
        selected_idx = self.trade_listbox.curselection()
        if len(selected_idx) != 1:
            messagebox.showwarning("提示", "请仅选中1个交易项进行修改！")
            return
        
        self.selected_edit_idx = selected_idx[0]
        target_trade = self.trades[self.selected_edit_idx]
        
        # 将目标交易项的参数填充到编辑框
        self.buy_id.delete(0, tk.END)
        self.buy_id.insert(0, target_trade["buy_id"])
        
        self.buy_count.delete(0, tk.END)
        self.buy_count.insert(0, target_trade["buy_count"])
        
        self.sell_id.delete(0, tk.END)
        self.sell_id.insert(0, target_trade["sell_id"])
        
        self.sell_count.delete(0, tk.END)
        self.sell_count.insert(0, target_trade["sell_count"])
        
        self.max_uses.delete(0, tk.END)
        self.max_uses.insert(0, target_trade["max_uses"])
        
        self.trade_type_var.set(target_trade["trade_type"])
        
        # 切换按钮状态：显示"修改交易项"和"取消修改"，隐藏"添加交易项"
        self.add_modify_btn.config(text="修改交易项")
        self.cancel_edit_btn.grid()  # 显示取消按钮
        
        # 滚动到编辑区域，方便用户操作
        self.trade_edit_frame.tkraise()

    def cancel_edit(self):
        """取消当前修改状态"""
        self.selected_edit_idx = None  # 清空待修改索引
        # 恢复按钮状态
        self.add_modify_btn.config(text="添加交易项")
        self.cancel_edit_btn.grid_remove()  # 隐藏取消按钮
        # 重置编辑框为默认值
        self.buy_id.delete(0, tk.END)
        self.buy_id.insert(0, "minecraft:emerald")
        self.buy_count.delete(0, tk.END)
        self.buy_count.insert(0, "1")
        self.sell_id.delete(0, tk.END)
        self.sell_id.insert(0, "minecraft:grass_block")
        self.sell_count.delete(0, tk.END)
        self.sell_count.insert(0, "1")
        self.max_uses.delete(0, tk.END)
        self.max_uses.insert(0, "256")
        self.trade_type_var.set("emerald_buy")

    def add_or_modify_trade(self):
        """添加新交易项 或 修改现有交易项（根据selected_edit_idx判断）"""
        # 获取输入并验证
        buy_id = self.buy_id.get().strip()
        sell_id = self.sell_id.get().strip()
        buy_count = self.buy_count.get().strip()
        sell_count = self.sell_count.get().strip()
        max_uses = self.max_uses.get().strip()
        
        # 基础验证
        if not all([buy_id, sell_id, buy_count, sell_count, max_uses]):
            messagebox.showerror("错误", "所有输入框不能为空！")
            return
        if not (buy_count.isdigit() and sell_count.isdigit() and max_uses.isdigit()):
            messagebox.showerror("错误", "数量和maxUses必须是正整数！")
            return
        if int(buy_count) <= 0 or int(sell_count) <= 0 or int(max_uses) <= 0:
            messagebox.showerror("错误", "数量和maxUses必须大于0！")
            return
        
        # 补全minecraft:前缀
        if not buy_id.startswith("minecraft:"):
            buy_id = f"minecraft:{buy_id}"
        if not sell_id.startswith("minecraft:"):
            sell_id = f"minecraft:{sell_id}"
        
        # 构建交易项字典
        trade_type = self.trade_type_var.get()
        new_trade = {
            "buy_id": buy_id,
            "buy_count": buy_count,
            "sell_id": sell_id,
            "sell_count": sell_count,
            "max_uses": max_uses,
            "trade_type": trade_type
        }
        
        # 判断是添加还是修改
        if self.selected_edit_idx is None:
            # 新增模式
            self.trades.append(new_trade)
            # messagebox.showinfo("成功", "交易项已添加！")
        else:
            # 修改模式：替换指定索引的交易项
            self.trades[self.selected_edit_idx] = new_trade
            messagebox.showinfo("成功", "交易项已修改！")
            # 取消修改状态
            self.cancel_edit()
        
        # 更新列表并重置编辑框
        self.update_trade_listbox()
        if self.selected_edit_idx is None:
            # 新增后重置编辑框（修改后已通过cancel_edit重置）
            self.buy_id.delete(0, tk.END)
            self.buy_id.insert(0, "minecraft:emerald")
            self.buy_count.delete(0, tk.END)
            self.buy_count.insert(0, "1")
            self.sell_id.delete(0, tk.END)
            self.sell_id.insert(0, "minecraft:grass_block")
            self.sell_count.delete(0, tk.END)
            self.sell_count.insert(0, "1")
            self.max_uses.delete(0, tk.END)
            self.max_uses.insert(0, "256")

    # ---------------------- 原有功能保持不变 ----------------------
    def delete_trade(self):
        """多选删除交易项"""
        selected_idx = self.trade_listbox.curselection()
        if not selected_idx:
            messagebox.showwarning("提示", "请选中要删除的交易项！")
            return
        
        # 若删除的是当前待修改项，先取消修改
        if self.selected_edit_idx in selected_idx:
            self.cancel_edit()
        
        # 逆序删除避免索引偏移
        for idx in sorted(selected_idx, reverse=True):
            del self.trades[idx]
        self.update_trade_listbox()

    def move_trade_up(self):
        """上移单个选中项"""
        selected_idx = self.trade_listbox.curselection()
        if len(selected_idx) != 1:
            messagebox.showwarning("提示", "请仅选中1个交易项上移！")
            return
        
        idx = selected_idx[0]
        if idx > 0:
            # 若移动的是待修改项，同步更新索引
            if self.selected_edit_idx == idx:
                self.selected_edit_idx = idx - 1
            elif self.selected_edit_idx == idx - 1:
                self.selected_edit_idx = idx
            
            self.trades[idx], self.trades[idx-1] = self.trades[idx-1], self.trades[idx]
            self.update_trade_listbox()
            self.trade_listbox.selection_clear(0, tk.END)
            self.trade_listbox.selection_set(idx-1)

    def move_trade_down(self):
        """下移单个选中项"""
        selected_idx = self.trade_listbox.curselection()
        if len(selected_idx) != 1:
            messagebox.showwarning("提示", "请仅选中1个交易项下移！")
            return
        
        idx = selected_idx[0]
        if idx < len(self.trades) - 1:
            # 若移动的是待修改项，同步更新索引
            if self.selected_edit_idx == idx:
                self.selected_edit_idx = idx + 1
            elif self.selected_edit_idx == idx + 1:
                self.selected_edit_idx = idx
            
            self.trades[idx], self.trades[idx+1] = self.trades[idx+1], self.trades[idx]
            self.update_trade_listbox()
            self.trade_listbox.selection_clear(0, tk.END)
            self.trade_listbox.selection_set(idx+1)

    def reverse_append_trades(self):
        """一键反转追加交易项"""
        if not self.trades:
            messagebox.showwarning("提示", "无交易项可反转！")
            return
        
        reversed_trades = []
        for trade in self.trades:
            reversed_trades.append({
                "buy_id": trade["sell_id"],
                "buy_count": trade["sell_count"],
                "sell_id": trade["buy_id"],
                "sell_count": trade["buy_count"],
                "max_uses": trade["max_uses"],
                "trade_type": "item_sell" if trade["trade_type"] == "emerald_buy" else "emerald_buy"
            })
        
        self.trades.extend(reversed_trades)
        self.update_trade_listbox()
        messagebox.showinfo("成功", f"已反转{len(reversed_trades)}个交易项并追加！")

    def save_config_to_json(self):
        """将当前配置保存到JSON文件"""
        config_data = {
            "villager_name": self.villager_name.get().strip() or "CustomName",
            "profession": self.profession_var.get(),
            "trades": self.trades
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
            self.villager_name.delete(0, tk.END)
            self.villager_name.insert(0, config_data["villager_name"])
            
            # 处理职业
            if config_data["profession"] in self.professions:
                self.profession_var.set(config_data["profession"])
            else:
                messagebox.showwarning("职业不匹配", f"配置中的职业{config_data['profession']}不存在，使用默认盔甲匠")
                self.profession_var.set("armorer")
            
            # 加载交易项并取消当前修改状态
            self.cancel_edit()
            self.trades = config_data["trades"]
            self.update_trade_listbox()
            
            messagebox.showinfo("成功", f"已加载配置：\n{os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("加载失败", f"错误信息：{str(e)}")

    def generate_command(self):
        """生成指令（limit=1] 与 set 间有两个空格）"""
        if not self.trades:
            messagebox.showwarning("提示", "请至少添加一个交易项！")
            return
        
        villager_name = self.villager_name.get().strip() or "CustomName"
        profession = self.profession_var.get()
        custom_name = f'{{"text":"{villager_name}"}}'
        
        # 构建交易列表NBT
        recipes = []
        for trade in self.trades:
            recipes.append(
                f'{{buy:{{id:"{trade["buy_id"]}",Count:{trade["buy_count"]}b}},'
                f'sell:{{id:"{trade["sell_id"]}",Count:{trade["sell_count"]}b}},'
                f'maxUses:{trade["max_uses"]}}}'
            )
        recipes_str = ",\n    ".join(recipes)
        
        # 生成指令（关键：limit=1] 后两个空格）
        command = (
            f'/data modify entity @e[type=villager,name="{villager_name}",limit=1]  set value {{\n  '
            f'CustomName:{custom_name},\n  '
            f'CustomNameVisible:1b,\n  '
            f'VillagerData:{{profession:{profession},level:5}},\n  '
            f'PersistenceRequired:1b,\n  '
            f'Offers:{{Recipes:[{recipes_str}]}}\n'
            f'}}'
        )
        
        # 显示指令
        self.command_text.config(state=tk.NORMAL)
        self.command_text.delete(1.0, tk.END)
        self.command_text.insert(1.0, command)
        self.command_text.config(state=tk.DISABLED)
        
        messagebox.showinfo("成功", "指令已生成！")

if __name__ == "__main__":
    root = tk.Tk()
    app = VillagerTradeGenerator(root)
    root.mainloop()
