## Copyright (c) 2025 Radium-bit
## SPDX-License-Identifier: GPL-V3
## See LICENSE file for full terms
import tkinter as tk
from tkinter import ttk, messagebox
from modules.trade_manager import TradeManager
from modules.nbt_handler import NbtHandler
from modules.command_generator import CommandGenerator
from modules.config_handler import ConfigHandler

class MainWindow:
    def __init__(self, root):
        # 初始化核心模块
        self.nbt_handler = NbtHandler()
        self.trade_manager = TradeManager()
        self.command_generator = CommandGenerator()
        self.config_handler = ConfigHandler(self)
        
        # 初始化主窗口
        self.root = root
        self.root.title("Minecraft村民交易指令生成器 v0.3 by.Radiumbit")
        self.root.geometry("1000x900")
        
        # 存储UI状态
        self.selected_edit_idx = None
        self.nbt_tooltip = None
        
        # 创建UI组件
        self.create_widgets()
        
        # 初始化默认数据
        self.trade_manager.init_default_trades()
        self.update_trade_listbox()

    def create_widgets(self):
        """创建所有UI组件"""
        # 顶部功能按钮栏
        self.create_top_buttons()
        
        # 村民基础信息区域
        self.create_villager_info_area()
        
        # 交易项编辑区域
        self.create_trade_editor_area()
        
        # 交易项列表区域
        self.create_trade_list_area()
        
        # 指令生成区域（选项卡版）
        self.create_command_generator_area()

    def create_top_buttons(self):
        """创建顶部功能按钮"""
        self.top_btn_frame = ttk.Frame(self.root)
        self.top_btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.save_btn = ttk.Button(
            self.top_btn_frame, 
            text="保存配置到JSON", 
            command=self.config_handler.save_config_to_json
        )
        self.save_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.load_btn = ttk.Button(
            self.top_btn_frame, 
            text="加载JSON预设", 
            command=self.config_handler.load_config_from_json
        )
        self.load_btn.pack(side=tk.LEFT, padx=2, pady=2)

    def create_villager_info_area(self):
        """创建村民基础信息区域"""
        self.villager_frame = ttk.LabelFrame(self.root, text="村民基础信息")
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

    def create_trade_editor_area(self):
        """创建交易项编辑区域"""
        self.trade_edit_frame = ttk.LabelFrame(self.root, text="交易项编辑（支持NBT标签，格式: 物品ID{标签}）")
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
        
        # Buy方物品（支持NBT标签）
        ttk.Label(self.trade_edit_frame, text="Buy方物品ID:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(self.trade_edit_frame, text="").grid(row=2, column=4, padx=5, pady=5, sticky=tk.W)
        self.buy_id = ttk.Entry(self.trade_edit_frame, width=50)
        self.buy_id.grid(row=2, column=1, padx=5, pady=5, columnspan=3)
        self.buy_id.insert(0, "minecraft:emerald")
        
        ttk.Label(self.trade_edit_frame, text="数量:").grid(row=2, column=5, padx=5, pady=5, sticky=tk.W)
        self.buy_count = ttk.Entry(self.trade_edit_frame, width=10)
        self.buy_count.grid(row=2, column=6, padx=5, pady=5)
        self.buy_count.insert(0, "1")
        
        # Sell方物品（支持NBT标签）
        ttk.Label(self.trade_edit_frame, text="Sell方物品ID:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(self.trade_edit_frame, text="").grid(row=3, column=4, padx=5, pady=5, sticky=tk.W)
        self.sell_id = ttk.Entry(self.trade_edit_frame, width=50)
        self.sell_id.grid(row=3, column=1, padx=5, pady=5, columnspan=3)
        self.sell_id.insert(0, "minecraft:grass_block")
        
        ttk.Label(self.trade_edit_frame, text="数量:").grid(row=3, column=5, padx=5, pady=5, sticky=tk.W)
        self.sell_count = ttk.Entry(self.trade_edit_frame, width=10)
        self.sell_count.grid(row=3, column=6, padx=5, pady=5)
        self.sell_count.insert(0, "1")
        
        # 最大交易次数
        ttk.Label(self.trade_edit_frame, text="最大交易次数(maxUses):").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.max_uses = ttk.Entry(self.trade_edit_frame, width=10)
        self.max_uses.grid(row=4, column=1, padx=5, pady=5)
        self.max_uses.insert(0, "256")
        
        # 添加/修改按钮
        self.add_modify_btn = ttk.Button(
            self.trade_edit_frame, 
            text="添加交易项", 
            command=self.add_or_modify_trade
        )
        self.add_modify_btn.grid(row=4, column=2, padx=5, pady=5)
        
        # 取消修改按钮
        self.cancel_edit_btn = ttk.Button(
            self.trade_edit_frame, 
            text="取消修改", 
            command=self.cancel_edit
        )
        self.cancel_edit_btn.grid(row=4, column=3, padx=5, pady=5)
        self.cancel_edit_btn.grid_remove()  # 初始隐藏

    def create_trade_list_area(self):
        """创建交易项列表区域"""
        self.trade_list_frame = ttk.LabelFrame(
            self.root, 
            text="已添加的交易项（右键列表项可修改参数，悬停NBT项查看详情）"
        )
        self.trade_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 列表操作按钮栏
        self.list_btn_frame = ttk.Frame(self.trade_list_frame)
        self.list_btn_frame.pack(fill=tk.X, padx=5, pady=3)
        
        self.reverse_btn = ttk.Button(
            self.list_btn_frame, 
            text="一键反转追加交易", 
            command=self.reverse_append_trades
        )
        self.reverse_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.move_up_btn = ttk.Button(
            self.list_btn_frame, 
            text="上移选中项", 
            command=self.move_trade_up
        )
        self.move_up_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.move_down_btn = ttk.Button(
            self.list_btn_frame, 
            text="下移选中项", 
            command=self.move_trade_down
        )
        self.move_down_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.del_btn = ttk.Button(
            self.list_btn_frame, 
            text="删除选中交易（支持多选）", 
            command=self.delete_trade
        )
        self.del_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # 列表框（支持多选+右键菜单+悬停预览）
        ttk.Label(
            self.list_btn_frame, 
            text="交易项预览：buy[ID:数量] → sell[ID:数量] | maxUses"
        ).pack(side=tk.LEFT, padx=10, pady=2)
        
        self.trade_listbox = tk.Listbox(
            self.trade_list_frame, 
            width=130, 
            height=12, 
            selectbackground="#4a86e8", 
            selectforeground="white", 
            selectmode=tk.EXTENDED
        )
        self.trade_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 绑定事件
        self.trade_listbox.bind("<Button-3>", self.show_trade_right_click_menu)
        self.trade_listbox.bind("<Motion>", self.on_listbox_motion)  # 鼠标移动事件
        self.trade_listbox.bind("<Leave>", self.on_listbox_leave)    # 鼠标离开列表事件
        
        # 初始化右键菜单
        self.trade_right_menu = tk.Menu(self.root, tearoff=0)
        self.trade_right_menu.add_command(
            label="修改此交易项", 
            command=self.start_edit_selected_trade
        )

    def create_command_generator_area(self):
        """创建指令生成区域"""
        self.result_frame = ttk.LabelFrame(
            self.root, 
            text="生成的指令（默认展示交易修改，其余为增强选项）"
        )
        self.result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.gen_btn = ttk.Button(
            self.result_frame, 
            text="生成指令", 
            command=self.generate_command
        )
        self.gen_btn.pack(anchor=tk.W, padx=5, pady=5)
        
        # 选项卡容器
        self.notebook = ttk.Notebook(self.result_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 存储每个选项卡的Text组件
        self.command_tabs = {}
        # 选项卡定义
        self.tab_definitions = [
            ("步骤1：设置村民自定义名称", "设置村民自定义名称"),
            ("步骤2：设置村民职业与等级", "修改村民职业和等级（固定5级）"),
            ("步骤3：设置永久驻留", "设置驻留确保村民不会被游戏自动卸载"),
            ("步骤4：设置名称可见", "设为1b显示村民头顶的自定义名称标签"),
            ("步骤5：设置交易列表", "修改村民的交易内容，核心功能，生成后直接复制使用")
        ]
        
        # 创建每个选项卡
        for tab_name, tab_desc in self.tab_definitions:
            tab_frame = ttk.Frame(self.notebook)
            self.notebook.add(tab_frame, text=tab_name)
            
            # 选项卡说明
            desc_label = ttk.Label(
                tab_frame, 
                text=f"说明：{tab_desc}", 
                wraplength=900, 
                justify=tk.LEFT
            )
            desc_label.pack(anchor=tk.W, padx=5, pady=2)
            
            # 命令显示文本框
            cmd_text = tk.Text(tab_frame, wrap=tk.WORD, width=130, height=10)
            cmd_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
            cmd_text.config(state=tk.DISABLED)
            self.command_tabs[tab_name] = cmd_text
            
            # 复制按钮
            copy_btn = ttk.Button(
                tab_frame, 
                text="复制命令到剪贴板", 
                command=lambda txt=cmd_text: self.copy_command_to_clipboard(txt)
            )
            copy_btn.pack(anchor=tk.W, padx=5, pady=3)
        
        # 设置默认选中最后一个选项卡
        self.notebook.select(len(self.tab_definitions) - 1)

    # ---------------------- 交易项管理相关方法 ----------------------
    def update_trade_listbox(self):
        """更新交易项列表框（显示NBT标识和哈希）"""
        self.trade_listbox.delete(0, tk.END)
        for idx, trade in enumerate(self.trade_manager.trades):
            # 解析buy方物品
            _, buy_nbt = self.nbt_handler.parse_item_with_nbt(trade["buy_id"])
            buy_id_simple = self.nbt_handler.simplify_item_id(trade["buy_id"])
            buy_hash = self.nbt_handler.get_nbt_hash(buy_nbt)
            buy_info = f"{buy_id_simple}:{trade['buy_count']}"
            if buy_nbt:
                buy_info += f" [NBT: {buy_hash}]"
            
            # 解析sell方物品
            _, sell_nbt = self.nbt_handler.parse_item_with_nbt(trade["sell_id"])
            sell_id_simple = self.nbt_handler.simplify_item_id(trade["sell_id"])
            sell_hash = self.nbt_handler.get_nbt_hash(sell_nbt)
            sell_info = f"{sell_id_simple}:{trade['sell_count']}"
            if sell_nbt:
                sell_info += f" [NBT: {sell_hash}]"
            
            # 构建列表项文本
            item_text = f"{idx+1}. buy[{buy_info}] → sell[{sell_info}] | maxUses:{trade['max_uses']}"
            
            # 设置背景色
            if trade["trade_type"] == "emerald_buy":
                final_bg = "#e8f8e8" if idx % 2 == 0 else "#d8e8d8"
            else:
                final_bg = "#f8e8f8" if idx % 2 == 0 else "#e8d8e8"
            
            self.trade_listbox.insert(tk.END, item_text)
            self.trade_listbox.itemconfig(idx, bg=final_bg)

    def swap_buy_sell_on_trade_type_switch(self):
        """切换交易类型时处理物品ID"""
        current_buy_id = self.buy_id.get().strip()
        current_buy_count = self.buy_count.get().strip()
        current_sell_id = self.sell_id.get().strip()
        current_sell_count = self.sell_count.get().strip()

        target_trade_type = self.trade_type_var.get()
        if target_trade_type == "emerald_buy":
            # 切换到“绿宝石买物品”
            new_buy_id = "minecraft:emerald"
            new_buy_count = current_buy_count
            new_sell_id = current_buy_id if current_buy_id != "minecraft:emerald" else current_sell_id
            new_sell_count = current_buy_count if current_buy_id != "minecraft:emerald" else current_sell_count
        else:
            # 切换到“物品换绿宝石”
            new_buy_id = current_sell_id
            new_buy_count = current_sell_count
            new_sell_id = "minecraft:emerald"
            new_sell_count = current_buy_count

        # 更新输入框
        self.buy_id.delete(0, tk.END)
        self.buy_id.insert(0, new_buy_id if new_buy_id else "minecraft:emerald")
        
        self.buy_count.delete(0, tk.END)
        self.buy_count.insert(0, new_buy_count if new_buy_count.isdigit() else "1")
        
        self.sell_id.delete(0, tk.END)
        self.sell_id.insert(0, new_sell_id if new_sell_id else "minecraft:grass_block")
        
        self.sell_count.delete(0, tk.END)
        self.sell_count.insert(0, new_sell_count if new_sell_count.isdigit() else "1")

    def show_trade_right_click_menu(self, event):
        click_idx = self.trade_listbox.nearest(event.y)
        if 0 <= click_idx < len(self.trade_manager.trades) and click_idx not in self.trade_listbox.curselection():
            self.trade_listbox.selection_clear(0, tk.END)
            self.trade_listbox.selection_set(click_idx)
        
        if len(self.trade_listbox.curselection()) == 1:
            self.trade_right_menu.post(event.x_root, event.y_root)

    def start_edit_selected_trade(self):
        selected_idx = self.trade_listbox.curselection()
        if len(selected_idx) != 1:
            messagebox.showwarning("提示", "请仅选中1个交易项进行修改！")
            return
        
        self.selected_edit_idx = selected_idx[0]
        target_trade = self.trade_manager.trades[self.selected_edit_idx]
        
        # 填充参数到编辑框
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
        
        # 切换按钮状态
        self.add_modify_btn.config(text="修改交易项")
        self.cancel_edit_btn.grid()
        self.trade_edit_frame.tkraise()

    def cancel_edit(self):
        self.selected_edit_idx = None
        self.add_modify_btn.config(text="添加交易项")
        self.cancel_edit_btn.grid_remove()
        # 重置编辑框
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
        """添加/修改交易项（增加NBT验证）"""
        # 获取并验证输入
        buy_id_input = self.buy_id.get().strip()
        sell_id_input = self.sell_id.get().strip()
        buy_count = self.buy_count.get().strip()
        sell_count = self.sell_count.get().strip()
        max_uses = self.max_uses.get().strip()
        
        if not all([buy_id_input, sell_id_input, buy_count, sell_count, max_uses]):
            messagebox.showerror("错误", "所有输入框不能为空！")
            return
        
        # 验证数量
        if not (buy_count.isdigit() and sell_count.isdigit() and max_uses.isdigit()):
            messagebox.showerror("错误", "数量和maxUses必须是正整数！")
            return
        if int(buy_count) <= 0 or int(sell_count) <= 0 or int(max_uses) <= 0:
            messagebox.showerror("错误", "数量和maxUses必须大于0！")
            return
        
        # 验证物品格式（尝试解析NBT）
        try:
            # 仅验证格式，不实际修改
            self.nbt_handler.parse_item_with_nbt(buy_id_input)
            self.nbt_handler.parse_item_with_nbt(sell_id_input)
        except ValueError as e:
            messagebox.showerror("物品格式错误", str(e))
            return
        
        # 构建交易项（保存原始输入，包含NBT标签）
        new_trade = {
            "buy_id": buy_id_input,
            "buy_count": buy_count,
            "sell_id": sell_id_input,
            "sell_count": sell_count,
            "max_uses": max_uses,
            "trade_type": self.trade_type_var.get()
        }
        
        # 新增/修改逻辑
        if self.selected_edit_idx is None:
            self.trade_manager.add_trade(new_trade)
        else:
            self.trade_manager.update_trade(self.selected_edit_idx, new_trade)
            messagebox.showinfo("成功", "交易项已修改！")
            self.cancel_edit()
        
        # 更新列表
        self.update_trade_listbox()
        if self.selected_edit_idx is None:
            # 新增后重置编辑框
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

    def delete_trade(self):
        selected_idx = self.trade_listbox.curselection()
        if not selected_idx:
            messagebox.showwarning("提示", "请选中要删除的交易项！")
            return
        
        if self.selected_edit_idx in selected_idx:
            self.cancel_edit()
        
        # 逆序删除避免索引偏移
        self.trade_manager.delete_trades(selected_idx)
        self.update_trade_listbox()

    def move_trade_up(self):
        selected_idx = self.trade_listbox.curselection()
        if len(selected_idx) != 1:
            messagebox.showwarning("提示", "请仅选中1个交易项上移！")
            return
        
        idx = selected_idx[0]
        if idx > 0:
            if self.selected_edit_idx == idx:
                self.selected_edit_idx = idx - 1
            elif self.selected_edit_idx == idx - 1:
                self.selected_edit_idx = idx
            
            self.trade_manager.swap_trades(idx, idx-1)
            self.update_trade_listbox()
            self.trade_listbox.selection_clear(0, tk.END)
            self.trade_listbox.selection_set(idx-1)

    def move_trade_down(self):
        selected_idx = self.trade_listbox.curselection()
        if len(selected_idx) != 1:
            messagebox.showwarning("提示", "请仅选中1个交易项下移！")
            return
        
        idx = selected_idx[0]
        if idx < len(self.trade_manager.trades) - 1:
            if self.selected_edit_idx == idx:
                self.selected_edit_idx = idx + 1
            elif self.selected_edit_idx == idx + 1:
                self.selected_edit_idx = idx
            
            self.trade_manager.swap_trades(idx, idx+1)
            self.update_trade_listbox()
            self.trade_listbox.selection_clear(0, tk.END)
            self.trade_listbox.selection_set(idx+1)

    def reverse_append_trades(self):
        if not self.trade_manager.trades:
            messagebox.showwarning("提示", "无交易项可反转！")
            return
        
        reversed_trades = self.trade_manager.reverse_trades()
        self.trade_manager.add_trades(reversed_trades)
        self.update_trade_listbox()
        messagebox.showinfo("成功", f"已反转{len(reversed_trades)}个交易项并追加！")

    # ---------------------- NBT悬停预览功能 ----------------------
    def show_nbt_tooltip(self, event, nbt_content, x, y):
        """显示NBT内容的浮动窗口"""
        # 如果已有浮窗则销毁
        self.hide_nbt_tooltip()
        
        # 创建新的顶级窗口作为浮窗
        self.nbt_tooltip = tk.Toplevel(self.root)
        self.nbt_tooltip.wm_overrideredirect(True)  # 无边框
        self.nbt_tooltip.wm_geometry(f"+{x}+{y}")   # 定位到鼠标位置
        
        # 添加标签显示NBT内容
        label = ttk.Label(
            self.nbt_tooltip, 
            text=f"NBT标签内容:\n{nbt_content}", 
            background="#ffffe0",  # 浅黄色背景
            relief=tk.SOLID, 
            borderwidth=1,
            wraplength=400,  # 自动换行
            justify=tk.LEFT
        )
        label.pack(padx=5, pady=5)
        
        # 绑定鼠标离开事件
        self.nbt_tooltip.bind("<Leave>", lambda e: self.hide_nbt_tooltip())

    def hide_nbt_tooltip(self):
        """隐藏NBT浮窗"""
        if self.nbt_tooltip:
            self.nbt_tooltip.destroy()
            self.nbt_tooltip = None

    def on_listbox_motion(self, event):
        """处理列表框上的鼠标移动事件"""
        # 获取鼠标位置对应的列表项
        index = self.trade_listbox.nearest(event.y)
        if 0 <= index < len(self.trade_manager.trades):
            # 获取当前交易项
            trade = self.trade_manager.trades[index]
            
            # 检查buy和sell物品是否有NBT标签
            _, buy_nbt = self.nbt_handler.parse_item_with_nbt(trade["buy_id"])
            _, sell_nbt = self.nbt_handler.parse_item_with_nbt(trade["sell_id"])
            
            # 获取鼠标在屏幕上的绝对位置
            x = self.root.winfo_pointerx() + 10
            y = self.root.winfo_pointery() + 10
            
            # 显示浮窗（优先显示sell方的NBT，如果没有则显示buy方的）
            if sell_nbt:
                self.show_nbt_tooltip(event, sell_nbt, x, y)
            elif buy_nbt:
                self.show_nbt_tooltip(event, buy_nbt, x, y)
            else:
                self.hide_nbt_tooltip()
        else:
            self.hide_nbt_tooltip()

    def on_listbox_leave(self, event):
        """处理鼠标离开列表框事件"""
        self.hide_nbt_tooltip()

    # ---------------------- 指令生成与复制功能 ----------------------
    def generate_command(self):
        if not self.trade_manager.trades:
            messagebox.showwarning("提示", "请至少添加一个交易项！")
            return
        
        villager_name = self.villager_name.get().strip() or "CustomName"
        profession = self.profession_var.get()
        
        # 生成所有步骤的指令
        commands = self.command_generator.generate_all_commands(
            villager_name, 
            profession, 
            self.trade_manager.trades,
            self.nbt_handler
        )
        
        # 将指令填充到对应选项卡
        for i, (tab_name, _) in enumerate(self.tab_definitions):
            self._fill_cmd_to_tab(tab_name, commands[i])
        
        messagebox.showinfo("成功", "所有指令已生成！默认展示交易修改选项卡。\n如果是第一次创建，请按选项卡顺序执行命令")

    def _fill_cmd_to_tab(self, tab_name, command):
        text_widget = self.command_tabs.get(tab_name)
        if not text_widget:
            return
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        text_widget.insert(1.0, command)
        text_widget.config(state=tk.DISABLED)

    def copy_command_to_clipboard(self, text_widget):
        self.root.clipboard_clear()
        cmd_content = text_widget.get(1.0, tk.END).strip()
        if not cmd_content:
            messagebox.showwarning("提示", "当前选项卡无指令可复制！")
            return
        self.root.clipboard_append(cmd_content)
        messagebox.showinfo("成功", "指令已复制到剪贴板！")
