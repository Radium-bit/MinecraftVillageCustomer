import tkinter as tk
from tkinter import ttk, messagebox
from modules.trade_manager import TradeManager
from modules.nbt_handler import NbtHandler
from modules.command_generator import CommandGenerator
from modules.config_handler import ConfigHandler
import json
from pathlib import Path
from PIL import Image, ImageTk


class MainWindow:
    def __init__(self, root):
        # 初始化核心模块
        self.nbt_handler = NbtHandler()
        self.trade_manager = TradeManager()
        self.command_generator = CommandGenerator()
        self.config_handler = ConfigHandler(self)
        
        # 初始化主窗口
        self.root = root
        self.root.title("Minecraft村民交易指令生成器 v0.3A by.Radiumbit")
        self.root.geometry("1200x900")  # 增加宽度以适应多列
        
        # 存储UI状态
        self.selected_edit_idx = None
        self.nbt_tooltip = None
        self.current_hover_item = None  # Treeview悬停行记录
        self.original_bg = {}  # 存储行原始背景色
        
        # 物品选择功能相关属性（完整保留移植）
        self.items_data = self._load_items_json()  # 加载物品ID-名称表
        self.icon_photo_refs = {}  # 用于保持图片引用，防止被垃圾回收
        self.selector_win = None    # 物品选择弹窗实例
        self.selector_target = ""   # 标记目标输入框（buy/buy2）
        self.icon_cache = {}  # 预缓存所有32x32图片：{item_id: PhotoImage对象}
        self.default_icon = None    # 默认图标
        self.filter_delay_id = None # 防抖计数器
        
        # 创建带滚动条的主容器（保留之前的整体滚动功能）
        self.create_scrollable_container()
        
        # 创建UI组件
        self.create_widgets()
        
        # 初始化默认数据
        self._preload_icons()  # 初始化时预加载所有图片
        self.trade_manager.init_default_trades()
        self.update_trade_listbox()

    def create_scrollable_container(self):
        """创建带滚动条的主容器，确保小屏幕可完整访问"""
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.main_frame)
        self.v_scrollbar = ttk.Scrollbar(
            self.main_frame, 
            orient=tk.VERTICAL, 
            command=self.canvas.yview
        )
        self.h_scrollbar = ttk.Scrollbar(
            self.main_frame, 
            orient=tk.HORIZONTAL, 
            command=self.canvas.xview
        )
        
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas.configure(
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set
        )
        
        self.content_frame = ttk.Frame(self.canvas)
        self.canvas_frame_id = self.canvas.create_window(
            (0, 0), 
            window=self.content_frame, 
            anchor=tk.NW
        )
        
        self.content_frame.bind("<Configure>", self._on_content_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_main_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_main_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_main_mousewheel)

    def _on_content_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_frame_id, width=event.width)

    def _on_main_mousewheel(self, event):
        if event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    def create_widgets(self):
        """创建所有UI组件"""
        # 顶部功能按钮栏
        self.create_top_buttons()
        # 村民基础信息区域
        self.create_villager_info_area()
        # 交易项编辑区域
        self.create_trade_editor_area()
        # 交易项列表区域（带图标多列Treeview）
        self.create_trade_list_area()
        # 指令生成区域（选项卡版）
        self.create_command_generator_area()

    def create_top_buttons(self):
        """创建顶部功能按钮"""
        self.top_btn_frame = ttk.Frame(self.content_frame)
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
        self.villager_frame = ttk.LabelFrame(self.content_frame, text="村民基础信息")
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
        self.trade_edit_frame = ttk.LabelFrame(self.content_frame, text="交易项编辑（支持NBT标签，格式: 物品ID{标签}）")
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
        
        # Buy方物品（支持NBT标签 + 选择按钮）
        ttk.Label(self.trade_edit_frame, text="Buy方物品ID:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.buy_id = ttk.Entry(self.trade_edit_frame, width=40)
        self.buy_id.grid(row=2, column=1, padx=5, pady=5, columnspan=2)
        self.buy_id.insert(0, "minecraft:emerald")
        # Buy选择按钮
        self.buy_select_btn = ttk.Button(
            self.trade_edit_frame, 
            text="选择", 
            command=lambda: self._open_item_selector(target="buy")
        )
        self.buy_select_btn.grid(row=2, column=3, padx=2, pady=5, sticky=tk.W)
        # Buy数量输入框
        ttk.Label(self.trade_edit_frame, text="数量:").grid(row=2, column=4, padx=5, pady=5, sticky=tk.W)
        self.buy_count = ttk.Entry(self.trade_edit_frame, width=10)
        self.buy_count.grid(row=2, column=5, padx=5, pady=5)
        self.buy_count.insert(0, "1")

        # Buy2方物品（支持NBT标签 + 选择按钮）
        ttk.Label(self.trade_edit_frame, text="Buy2方物品ID:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Label(self.trade_edit_frame, text="(默认空气)").grid(row=3, column=4, padx=5, pady=5, sticky=tk.W)
        self.buy2_id = ttk.Entry(self.trade_edit_frame, width=40)
        self.buy2_id.grid(row=3, column=1, padx=5, pady=5, columnspan=2)
        self.buy2_id.insert(0, "minecraft:air")
        # Buy2选择按钮
        self.buy2_select_btn = ttk.Button(
            self.trade_edit_frame, 
            text="选择", 
            command=lambda: self._open_item_selector(target="buy2")
        )
        self.buy2_select_btn.grid(row=3, column=3, padx=2, pady=5, sticky=tk.W)
        # Buy2数量输入框
        ttk.Label(self.trade_edit_frame, text="数量:").grid(row=3, column=4, padx=5, pady=5, sticky=tk.W)
        self.buy2_count = ttk.Entry(self.trade_edit_frame, width=10)
        self.buy2_count.grid(row=3, column=5, padx=5, pady=5)
        self.buy2_count.insert(0, "1")
        
        # Sell方物品（支持NBT标签）
        ttk.Label(self.trade_edit_frame, text="Sell方物品ID:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.sell_id = ttk.Entry(self.trade_edit_frame, width=40)
        self.sell_id.grid(row=4, column=1, padx=5, pady=5, columnspan=2)
        self.sell_id.insert(0, "minecraft:grass_block")
        # Sell数量输入框
        ttk.Label(self.trade_edit_frame, text="数量:").grid(row=4, column=4, padx=5, pady=5, sticky=tk.W)
        self.sell_count = ttk.Entry(self.trade_edit_frame, width=10)
        self.sell_count.grid(row=4, column=5, padx=5, pady=5)
        self.sell_count.insert(0, "1")
        
        # 最大交易次数
        ttk.Label(self.trade_edit_frame, text="最大交易次数(maxUses):").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        self.max_uses = ttk.Entry(self.trade_edit_frame, width=10)
        self.max_uses.grid(row=5, column=1, padx=5, pady=5)
        self.max_uses.insert(0, "256")
        
        # 添加/修改按钮
        self.add_modify_btn = ttk.Button(
            self.trade_edit_frame, 
            text="添加交易项", 
            command=self.add_or_modify_trade
        )
        self.add_modify_btn.grid(row=5, column=2, padx=5, pady=5)
        
        # 取消修改按钮
        self.cancel_edit_btn = ttk.Button(
            self.trade_edit_frame, 
            text="取消修改", 
            command=self.cancel_edit
        )
        self.cancel_edit_btn.grid(row=5, column=3, padx=5, pady=5)
        self.cancel_edit_btn.grid_remove()  # 初始隐藏

    def create_trade_list_area(self):
        """创建交易项列表区域（带图标多列Treeview）"""
        self.trade_list_frame = ttk.LabelFrame(
            self.content_frame, 
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
        
        # 水平和垂直滚动条
        scroll_frame = ttk.Frame(self.trade_list_frame)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        self.trade_v_scroll = ttk.Scrollbar(scroll_frame, orient=tk.VERTICAL)
        self.trade_h_scroll = ttk.Scrollbar(scroll_frame, orient=tk.HORIZONTAL)
        
        # 配置多列Treeview（带图标）
        style = ttk.Style()
        style.configure("Treeview", rowheight=36)  # 适配32x32图标高度
        self.trade_listbox = ttk.Treeview(
            scroll_frame,
            columns=(
                "buy_icon", "buy_item", "buy_count",
                "buy2_icon", "buy2_item", "buy2_count",
                "arrow",
                "sell_icon", "sell_item", "sell_count",
                "max_uses"
            ),
            show="headings",
            yscrollcommand=self.trade_v_scroll.set,
            xscrollcommand=self.trade_h_scroll.set,
            selectmode=tk.EXTENDED
        )
        
        # 配置列标题和宽度
        self.trade_listbox.heading("buy_icon", text="Buy物品")
        self.trade_listbox.heading("buy_item", text="物品ID")
        self.trade_listbox.heading("buy_count", text="数量")
        self.trade_listbox.heading("buy2_icon", text="Buy2物品")
        self.trade_listbox.heading("buy2_item", text="物品ID")
        self.trade_listbox.heading("buy2_count", text="数量")
        self.trade_listbox.heading("arrow", text="")
        self.trade_listbox.heading("sell_icon", text="Sell物品")
        self.trade_listbox.heading("sell_item", text="物品ID")
        self.trade_listbox.heading("sell_count", text="数量")
        self.trade_listbox.heading("max_uses", text="最大可售")
        
        # 配置列宽
        self.trade_listbox.column("buy_icon", width=40, minwidth=40, stretch=False)
        self.trade_listbox.column("buy_item", width=150, minwidth=100)
        self.trade_listbox.column("buy_count", width=60, minwidth=50, stretch=False)
        self.trade_listbox.column("buy2_icon", width=40, minwidth=40, stretch=False)
        self.trade_listbox.column("buy2_item", width=150, minwidth=100)
        self.trade_listbox.column("buy2_count", width=60, minwidth=50, stretch=False)
        self.trade_listbox.column("arrow", width=30, minwidth=30, stretch=False)
        self.trade_listbox.column("sell_icon", width=40, minwidth=40, stretch=False)
        self.trade_listbox.column("sell_item", width=150, minwidth=100)
        self.trade_listbox.column("sell_count", width=60, minwidth=50, stretch=False)
        self.trade_listbox.column("max_uses", width=80, minwidth=70, stretch=False)
        
        # 放置Treeview和滚动条
        self.trade_listbox.grid(row=0, column=0, sticky=tk.NSEW)
        self.trade_v_scroll.grid(row=0, column=1, sticky=tk.NS)
        self.trade_h_scroll.grid(row=1, column=0, sticky=tk.EW)
        
        scroll_frame.grid_rowconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        self.trade_v_scroll.config(command=self.trade_listbox.yview)
        self.trade_h_scroll.config(command=self.trade_listbox.xview)
        
        # 绑定事件（含滚动优先级、右键菜单）
        self.trade_listbox.bind("<MouseWheel>", self._on_trade_list_mousewheel)
        self.trade_listbox.bind("<Button-4>", self._on_trade_list_mousewheel)
        self.trade_listbox.bind("<Button-5>", self._on_trade_list_mousewheel)
        self.trade_listbox.bind("<Button-3>", self.show_trade_right_click_menu)
        self.trade_listbox.bind("<Motion>", self.on_treeview_motion)
        self.trade_listbox.bind("<Leave>", self.on_treeview_leave)
        
        # 初始化右键菜单
        self.trade_right_menu = tk.Menu(self.root, tearoff=0)
        self.trade_right_menu.add_command(
            label="修改此交易项", 
            command=self.start_edit_selected_trade
        )

    def _on_trade_list_mousewheel(self, event):
        """交易列表内部滚动优先级处理：边界外允许外部滚动"""
        current_pos = self.trade_listbox.yview()
        is_at_top = current_pos[0] <= 0.0
        is_at_bottom = current_pos[1] >= 1.0

        delta = 0
        if event.delta:
            delta = int(-1 * (event.delta / 120))
        elif event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1

        if (delta < 0 and not is_at_top) or (delta > 0 and not is_at_bottom):
            self.trade_listbox.yview_scroll(delta, "units")
            return "break"

    def create_command_generator_area(self):
        """创建指令生成区域"""
        self.result_frame = ttk.LabelFrame(
            self.content_frame, 
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

    # ---------------------- 物品选择弹窗相关方法（完整移植） ----------------------
    def _preload_icons(self):
        """预加载所有物品图片到缓存"""
        icon_dir = Path(__file__).parent / "res" / "minecraft_icons"
        default_icon_path = icon_dir / "ItemSprite_default.png"
        # 预加载默认图标
        try:
            if default_icon_path.exists():
                img = Image.open(default_icon_path).resize((32, 32), Image.Resampling.LANCZOS)
                self.default_icon = ImageTk.PhotoImage(img)
                self.icon_photo_refs["default"] = self.default_icon  # 保存引用
            else:
                # 创建透明默认图标
                self.default_icon = ImageTk.PhotoImage(Image.new("RGBA", (32, 32), (0, 0, 0, 0)))
                self.icon_photo_refs["default"] = self.default_icon  # 保存引用
        except Exception as e:
            print(f"预加载默认图标失败: {e}")
            self.default_icon = ImageTk.PhotoImage(Image.new("RGBA", (32, 32), (0, 0, 0, 0)))
            self.icon_photo_refs["default"] = self.default_icon  # 保存引用
        # 预加载所有物品图标
        for item in self.items_data:
            item_id = item["ID"]
            try:
                icon_path = icon_dir / f"ItemSprite_{item_id}.png"
                if icon_path.exists():
                    img = Image.open(icon_path).resize((32, 32), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.icon_cache[item_id] = photo
                    self.icon_photo_refs[item_id] = photo  # 保存引用防止被回收
                else:
                    # 不存在时使用默认图标
                    self.icon_cache[item_id] = self.default_icon
            except Exception as e:
                print(f"预加载图标 {item_id} 失败: {e}")
                self.icon_cache[item_id] = self.default_icon

    def _filter_items(self, event=None):
        """带防抖的过滤方法"""
        if self.filter_delay_id and self.selector_win:
            self.selector_win.after_cancel(self.filter_delay_id)
        
        if self.selector_win:
            self.filter_delay_id = self.selector_win.after(
                300,
                lambda: self._load_items_to_tree(self.search_entry.get().strip())
            )

    def _load_items_json(self):
        """加载res/Items_ZH.json物品ID-名称对应表"""
        items_path = Path(__file__).parent / "res" / "Items_ZH.json"
        try:
            with open(items_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                return [item for item in raw_data if item.get("ID") and item.get("Name")]
        except FileNotFoundError:
            messagebox.showerror("错误", f"未找到物品配置文件：\n{items_path}")
            return []
        except json.JSONDecodeError:
            messagebox.showerror("错误", "Items_ZH.json格式错误（请检查JSON语法）")
            return []

    def _open_item_selector(self, target):
        """打开物品选择弹窗"""
        if self.selector_win:
            self.selector_win.destroy()
        
        self.selector_win = tk.Toplevel(self.root)
        self.selector_win.title("选择物品")
        self.selector_win.geometry("650x500")
        self.selector_win.resizable(True, True)
        self.selector_target = target

        # 搜索框
        search_frame = ttk.Frame(self.selector_win)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(search_frame, text="搜索（名称/ID）：").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=60)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.search_entry.focus()
        self.search_entry.bind("<KeyRelease>", self._filter_items)

        # 物品列表（带图标#0列）
        list_frame = ttk.Frame(self.selector_win)
        list_frame.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)
        
        v_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        style = ttk.Style()
        style.configure("Treeview", rowheight=36)
        
        self.item_tree = ttk.Treeview(
            list_frame,
            columns=("info"),
            show="headings tree",  # 显示#0图标列和info内容列
            yscrollcommand=v_scroll.set,
            selectmode="browse"
        )
        
        self.item_tree.heading("#0", text="")  # 图标列无标题
        self.item_tree.heading("info", text="物品名称（ID）", anchor=tk.W)
        self.item_tree.column("#0", width=60, minwidth=60, stretch=False)  # 图标列宽度
        self.item_tree.column("info", width=550, minwidth=200)
        self.item_tree.pack(fill=tk.BOTH, expand=True)
        v_scroll.config(command=self.item_tree.yview)

        # 确认按钮
        confirm_btn = ttk.Button(
            self.selector_win,
            text="确认选择",
            command=self._confirm_item_selection
        )
        confirm_btn.pack(pady=5)

        # 窗口关闭事件（清理引用）
        def on_close():
            self.icon_photo_refs.clear()
            self.selector_win.destroy()
            self.selector_win = None
        self.selector_win.protocol("WM_DELETE_WINDOW", on_close)

        # 初始加载所有物品
        self._load_items_to_tree()

        # 双击物品直接确认选择
        self.item_tree.bind("<Double-1>", lambda e: self._confirm_item_selection())

        # ---------------------- 新增：阻止滚动事件冒泡 ----------------------
        # 为物品选择弹窗的Treeview绑定滚动事件
        self.item_tree.bind("<MouseWheel>", self._on_selector_scroll)
        self.item_tree.bind("<Button-4>", self._on_selector_scroll)  # Linux滚轮上滚
        self.item_tree.bind("<Button-5>", self._on_selector_scroll)  # Linux滚轮下滚
        # 为滚动条绑定同样的事件处理，确保滚动条操作也不会冒泡
        v_scroll.bind("<MouseWheel>", self._on_selector_scroll)
        v_scroll.bind("<Button-4>", self._on_selector_scroll)
        v_scroll.bind("<Button-5>", self._on_selector_scroll)

    def _on_selector_scroll(self, event):
        """
        物品选择弹窗的滚动事件处理函数
        处理滚动并阻止事件冒泡到主窗口
        """
        # 处理Windows系统鼠标滚轮
        if event.delta:
            # 计算滚动方向和距离
            delta = int(-1 * (event.delta / 120))
            self.item_tree.yview_scroll(delta, "units")
        # 处理Linux系统鼠标滚轮
        elif event.num == 4:
            self.item_tree.yview_scroll(-1, "units")  # 上滚
        elif event.num == 5:
            self.item_tree.yview_scroll(1, "units")   # 下滚
        
        # 关键：返回"break"阻止事件继续传播到父窗口
        return "break"

    def _load_items_to_tree(self, filter_text=""):
        """加载物品到Treeview（带图标）"""
        for item in self.item_tree.get_children():
            self.item_tree.delete(item)
        
        for item in self.items_data:
            item_id = item["ID"]
            item_name = item["Name"]
            full_item_id = f"minecraft:{item_id}"

            # 过滤逻辑：匹配名称或ID
            if filter_text and not (
                filter_text.lower() in item_name.lower() or
                filter_text.lower() in item_id.lower()
            ):
                continue

            # 获取预缓存的图标
            photo = self.icon_cache.get(item_id, self.default_icon)
            info_text = f"{item_name}({full_item_id})"
            
            # 插入Treeview：#0列显示图标，info列显示名称和ID
            self.item_tree.insert(
                "", tk.END,
                image=photo,    # #0列图标
                text="",        # #0列文本留空
                values=(info_text,),  # info列内容
                tags=(full_item_id,)  # 存储完整物品ID用于后续选择
            )

    def _confirm_item_selection(self):
        """确认选择，将物品ID填入目标输入框"""
        selected_items = self.item_tree.selection()
        if not selected_items:
            messagebox.showwarning("提示", "请先选择一个物品！")
            return

        # 获取选中项的完整物品ID
        selected_item_id = self.item_tree.item(selected_items[0], "tags")[0]

        # 根据目标输入框填充ID
        if self.selector_target == "buy":
            self.buy_id.delete(0, tk.END)
            self.buy_id.insert(0, selected_item_id)
        elif self.selector_target == "buy2":
            self.buy2_id.delete(0, tk.END)
            self.buy2_id.insert(0, selected_item_id)

        # 关闭弹窗
        self.selector_win.destroy()
        self.selector_win = None

    # ---------------------- 交易项管理相关方法 ----------------------
    def update_trade_listbox(self):
        """更新交易项列表（带图标多列展示）"""
        # 保存滚动位置和选中状态
        scroll_pos = self.trade_listbox.yview()[0]
        h_scroll_pos = self.trade_listbox.xview()[0]
        selected_ids = self.trade_listbox.selection()

        # 清空现有数据
        for item in self.trade_listbox.get_children():
            self.trade_listbox.delete(item)
        self.original_bg.clear()

        # 遍历交易项并添加到Treeview
        for idx, trade in enumerate(self.trade_manager.trades):
            # 解析Buy方物品
            buy_id_full = trade["buy_id"]
            _, buy_nbt = self.nbt_handler.parse_item_with_nbt(buy_id_full)
            buy_id_simple = self.nbt_handler.simplify_item_id(buy_id_full)
            buy_hash = self.nbt_handler.get_nbt_hash(buy_nbt)
            buy_item_id = buy_id_simple.split(":")[-1] if ":" in buy_id_simple else buy_id_simple
            buy_photo = self.icon_cache.get(buy_item_id, self.default_icon)
            buy_item_text = buy_id_simple + (f" [NBT: {buy_hash}]" if buy_nbt else "")
            
            # 解析Buy2方物品
            buy2_id_full = trade.get("buy2_id", "minecraft:air")
            _, buy2_nbt = self.nbt_handler.parse_item_with_nbt(buy2_id_full)
            buy2_id_simple = self.nbt_handler.simplify_item_id(buy2_id_full)
            buy2_hash = self.nbt_handler.get_nbt_hash(buy2_nbt)
            buy2_item_id = buy2_id_simple.split(":")[-1] if ":" in buy2_id_simple else buy2_id_simple
            buy2_photo = self.icon_cache.get(buy2_item_id, self.default_icon)
            buy2_show = buy2_id_simple != "minecraft:air" or trade.get("buy2_count", "1") != "1"
            buy2_item_text = (buy2_id_simple + (f" [NBT: {buy2_hash}]" if buy2_nbt else "")) if buy2_show else ""
            buy2_count = trade.get("buy2_count", "1") if buy2_show else ""
            
            # 解析Sell方物品
            sell_id_full = trade["sell_id"]
            _, sell_nbt = self.nbt_handler.parse_item_with_nbt(sell_id_full)
            sell_id_simple = self.nbt_handler.simplify_item_id(sell_id_full)
            sell_hash = self.nbt_handler.get_nbt_hash(sell_nbt)
            sell_item_id = sell_id_simple.split(":")[-1] if ":" in sell_id_simple else sell_id_simple
            sell_photo = self.icon_cache.get(sell_item_id, self.default_icon)
            sell_item_text = sell_id_simple + (f" [NBT: {sell_hash}]" if sell_nbt else "")
            
            # 设置行背景色（交替色）
            bg_color = "#e8f8e8" if (trade["trade_type"] == "emerald_buy" and idx % 2 == 0) else \
                    "#d8e8d8" if trade["trade_type"] == "emerald_buy" else \
                    "#f8e8f8" if idx % 2 == 0 else "#e8d8e8"
            
            # 插入Treeview行 - 修复：使用image参数仅设置#0列图标
            tree_item_id = self.trade_listbox.insert(
                "", tk.END,
                image=buy_photo,  # 仅为#0列设置图标
                values=(
                    "",  # buy_icon列
                    buy_item_text,
                    trade["buy_count"],
                    "",  # buy2_icon列
                    buy2_item_text,
                    buy2_count,
                    "→",  # 箭头符号
                    "",  # sell_icon列
                    sell_item_text,
                    trade["sell_count"],
                    trade["max_uses"]
                ),
                tags=(str(idx),)
            )
            
            # 为其他列设置图标 - 修复：使用set方法而不是item方法
            self.trade_listbox.set(tree_item_id, "buy2_icon", "")
            self.trade_listbox.set(tree_item_id, "sell_icon", "")
            
            # 使用标签样式为不同列设置图标
            self.trade_listbox.tag_configure(f"buy2_{tree_item_id}", image=buy2_photo)
            self.trade_listbox.tag_configure(f"sell_{tree_item_id}", image=sell_photo)
            self.trade_listbox.item(tree_item_id, tags=(str(idx), f"buy2_{tree_item_id}", f"sell_{tree_item_id}"))
            
            # 保存原始背景色并应用
            self.original_bg[tree_item_id] = bg_color
            self.trade_listbox.tag_configure(str(idx), background=bg_color)
        
        # 恢复选中状态
        for tree_id in selected_ids:
            try:
                original_idx = self.trade_listbox.item(tree_id, "tags")[0]
                for new_tree_id in self.trade_listbox.get_children():
                    if self.trade_listbox.item(new_tree_id, "tags")[0] == original_idx:
                        self.trade_listbox.selection_add(new_tree_id)
                        break
            except Exception:
                continue
        
        # 恢复滚动位置
        self.trade_listbox.yview_moveto(scroll_pos)
        self.trade_listbox.xview_moveto(h_scroll_pos)


    def swap_buy_sell_on_trade_type_switch(self):
        """切换交易类型时处理物品ID"""
        current_buy_id = self.buy_id.get().strip()
        current_buy_count = self.buy_count.get().strip()
        current_sell_id = self.sell_id.get().strip()
        current_sell_count = self.sell_count.get().strip()

        target_trade_type = self.trade_type_var.get()
        if target_trade_type == "emerald_buy":
            new_buy_id = "minecraft:emerald"
            new_buy_count = current_buy_count
            new_sell_id = current_buy_id if current_buy_id != "minecraft:emerald" else current_sell_id
            new_sell_count = current_buy_count if current_buy_id != "minecraft:emerald" else current_sell_count
        else:
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
        """右键菜单：取消多选，仅选中当前行"""
        tree_item = self.trade_listbox.identify_row(event.y)
        if not tree_item:
            return
        
        try:
            # 模拟左键单击取消多选
            self.trade_listbox.event_generate("<Button-1>", x=event.x, y=event.y)
            self.trade_listbox.event_generate("<ButtonRelease-1>", x=event.x, y=event.y)
            click_idx = int(self.trade_listbox.item(tree_item, "tags")[0])
        except (IndexError, ValueError):
            return
        
        # 单选时显示菜单
        if len(self.trade_listbox.selection()) == 1:
            self.trade_right_menu.post(event.x_root, event.y_root)

    def start_edit_selected_trade(self):
        """右键修改交易项"""
        selected_items = self.trade_listbox.selection()
        if len(selected_items) != 1:
            return
        
        try:
            idx = int(self.trade_listbox.item(selected_items[0], "tags")[0])
        except (IndexError, ValueError):
            return
        
        trade = self.trade_manager.trades[idx]
        
        # 填充表单
        self.buy_id.delete(0, tk.END)
        self.buy_id.insert(0, trade["buy_id"])
        self.buy_count.delete(0, tk.END)
        self.buy_count.insert(0, trade["buy_count"])
        self.buy2_id.delete(0, tk.END)
        self.buy2_id.insert(0, trade.get("buy2_id", "minecraft:air"))
        self.buy2_count.delete(0, tk.END)
        self.buy2_count.insert(0, trade.get("buy2_count", "1"))
        self.sell_id.delete(0, tk.END)
        self.sell_id.insert(0, trade["sell_id"])
        self.sell_count.delete(0, tk.END)
        self.sell_count.insert(0, trade["sell_count"])
        self.max_uses.delete(0, tk.END)
        self.max_uses.insert(0, trade["max_uses"])
        
        self.selected_edit_idx = idx
        self.add_modify_btn.config(text="修改交易项")
        self.cancel_edit_btn.grid()

    def cancel_edit(self):
        """取消修改"""
        self.selected_edit_idx = None
        self.add_modify_btn.config(text="添加交易项")
        self.cancel_edit_btn.grid_remove()
        # 重置编辑框
        self.buy_id.delete(0, tk.END)
        self.buy_id.insert(0, "minecraft:emerald")
        self.buy_count.delete(0, tk.END)
        self.buy_count.insert(0, "1")
        self.buy2_id.delete(0, tk.END)
        self.buy2_id.insert(0, "minecraft:air")
        self.buy2_count.delete(0, tk.END)
        self.buy2_count.insert(0, "1")
        self.sell_id.delete(0, tk.END)
        self.sell_id.insert(0, "minecraft:grass_block")
        self.sell_count.delete(0, tk.END)
        self.sell_count.insert(0, "1")
        self.max_uses.delete(0, tk.END)
        self.max_uses.insert(0, "256")
        self.trade_type_var.set("emerald_buy")

    def add_or_modify_trade(self):
        """添加/修改交易项"""
        # 获取并验证输入
        buy_id_input = self.buy_id.get().strip()
        buy2_id_input = self.buy2_id.get().strip() or "minecraft:air"
        sell_id_input = self.sell_id.get().strip()
        buy_count = self.buy_count.get().strip()
        buy2_count = self.buy2_count.get().strip() or "1"
        sell_count = self.sell_count.get().strip()
        max_uses = self.max_uses.get().strip()
        
        # 验证必填字段
        if not all([buy_id_input, sell_id_input, buy_count, sell_count, max_uses, buy2_count]):
            messagebox.showerror("错误", "所有输入框不能为空！")
            return
        
        # 验证数量为正整数
        try:
            if int(buy_count) <= 0 or int(buy2_count) <= 0 or int(sell_count) <= 0 or int(max_uses) <= 0:
                messagebox.showerror("错误", "数量和maxUses必须大于0！")
                return
        except ValueError:
            messagebox.showerror("错误", "数量和maxUses必须是正整数！")
            return
        
        # 验证物品格式
        try:
            self.nbt_handler.parse_item_with_nbt(buy_id_input)
            self.nbt_handler.parse_item_with_nbt(buy2_id_input)
            self.nbt_handler.parse_item_with_nbt(sell_id_input)
        except ValueError as e:
            messagebox.showerror("物品格式错误", str(e))
            return
        
        # 构建交易项
        new_trade = {
            "buy_id": buy_id_input,
            "buy_count": buy_count,
            "buy2_id": buy2_id_input,
            "buy2_count": buy2_count,
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
            self.buy2_id.delete(0, tk.END)
            self.buy2_id.insert(0, "minecraft:air")
            self.buy2_count.delete(0, tk.END)
            self.buy2_count.insert(0, "1")
            self.sell_id.delete(0, tk.END)
            self.sell_id.insert(0, "minecraft:grass_block")
            self.sell_count.delete(0, tk.END)
            self.sell_count.insert(0, "1")
            self.max_uses.delete(0, tk.END)
            self.max_uses.insert(0, "256")

    def delete_trade(self):
        """删除交易项"""
        selected_items = self.trade_listbox.selection()
        if not selected_items:
            messagebox.showwarning("提示", "请选中要删除的交易项！")
            return
        
        # 获取选中项的索引（逆序删除）
        selected_indices = []
        for tree_id in selected_items:
            try:
                idx = int(self.trade_listbox.item(tree_id, "tags")[0])
                selected_indices.append(idx)
            except (IndexError, ValueError):
                continue
        
        # 取消正在编辑的项
        if self.selected_edit_idx in selected_indices:
            self.cancel_edit()
        
        # 删除交易项
        self.trade_manager.delete_trades(sorted(selected_indices, reverse=True))
        self.update_trade_listbox()

    def move_trade_up(self):
        """上移交易项"""
        selected_items = self.trade_listbox.selection()
        if len(selected_items) != 1:
            messagebox.showwarning("提示", "请仅选中1个交易项上移！")
            return
        
        try:
            idx = int(self.trade_listbox.item(selected_items[0], "tags")[0])
        except (IndexError, ValueError):
            return
        
        if idx <= 0:
            return
        
        # 更新编辑索引
        if self.selected_edit_idx == idx:
            self.selected_edit_idx = idx - 1
        elif self.selected_edit_idx == idx - 1:
            self.selected_edit_idx = idx
        
        # 交换交易项并更新列表
        self.trade_manager.swap_trades(idx, idx - 1)
        self.update_trade_listbox()
        
        # 重新选中移动后的项
        for tree_id in self.trade_listbox.get_children():
            if self.trade_listbox.item(tree_id, "tags")[0] == str(idx - 1):
                self.trade_listbox.selection_clear()
                self.trade_listbox.selection_add(tree_id)
                break

    def move_trade_down(self):
        """下移交易项"""
        selected_items = self.trade_listbox.selection()
        if len(selected_items) != 1:
            messagebox.showwarning("提示", "请仅选中1个交易项下移！")
            return
        
        try:
            idx = int(self.trade_listbox.item(selected_items[0], "tags")[0])
        except (IndexError, ValueError):
            return
        
        if idx >= len(self.trade_manager.trades) - 1:
            return
        
        # 更新编辑索引
        if self.selected_edit_idx == idx:
            self.selected_edit_idx = idx + 1
        elif self.selected_edit_idx == idx + 1:
            self.selected_edit_idx = idx
        
        # 交换交易项并更新列表
        self.trade_manager.swap_trades(idx, idx + 1)
        self.update_trade_listbox()
        
        # 重新选中移动后的项
        for tree_id in self.trade_listbox.get_children():
            if self.trade_listbox.item(tree_id, "tags")[0] == str(idx + 1):
                self.trade_listbox.selection_clear()
                self.trade_listbox.selection_add(tree_id)
                break

    def reverse_append_trades(self):
        """反转追加交易项"""
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
        self.hide_nbt_tooltip()
        
        self.nbt_tooltip = tk.Toplevel(self.root)
        self.nbt_tooltip.wm_overrideredirect(True)
        self.nbt_tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(
            self.nbt_tooltip, 
            text=f"NBT标签内容:\n{nbt_content}", 
            background="#ffffe0",
            relief=tk.SOLID, 
            borderwidth=1,
            wraplength=400,
            justify=tk.LEFT
        )
        label.pack(padx=5, pady=5)
        
        self.nbt_tooltip.bind("<Leave>", lambda e: self.hide_nbt_tooltip())

    def hide_nbt_tooltip(self):
        """隐藏NBT浮窗"""
        if self.nbt_tooltip:
            self.nbt_tooltip.destroy()
            self.nbt_tooltip = None

    def on_treeview_motion(self, event):
        """处理Treeview鼠标移动事件（悬停背景+NBT预览）"""
        tree_item = self.trade_listbox.identify_row(event.y)
        column = self.trade_listbox.identify_column(event.x)
        
        if not tree_item:
            self.hide_nbt_tooltip()
            self.reset_hover_bg()
            self.current_hover_item = None
            return
        
        # 处理悬停背景色
        if tree_item != self.current_hover_item:
            self.reset_hover_bg()
            self.current_hover_item = tree_item
            self.trade_listbox.tag_configure("hover", background="#ffffcc")
            self.trade_listbox.item(tree_item, tags=(*self.trade_listbox.item(tree_item, "tags"), "hover"))
        
        # 获取交易项索引并验证
        try:
            idx = int(self.trade_listbox.item(tree_item, "tags")[0])
        except (IndexError, ValueError):
            self.hide_nbt_tooltip()
            return
        
        if idx < 0 or idx >= len(self.trade_manager.trades):
            self.hide_nbt_tooltip()
            return
        
        # 解析NBT内容（根据当前列）
        trade = self.trade_manager.trades[idx]
        nbt_content = None
        if column == "#2":  # buy_item列
            _, nbt_content = self.nbt_handler.parse_item_with_nbt(trade["buy_id"])
        elif column == "#5":  # buy2_item列
            _, nbt_content = self.nbt_handler.parse_item_with_nbt(trade.get("buy2_id", "minecraft:air"))
        elif column == "#9":  # sell_item列
            _, nbt_content = self.nbt_handler.parse_item_with_nbt(trade["sell_id"])
        
        # 显示NBT预览浮窗
        if nbt_content:
            x = self.root.winfo_pointerx() + 10
            y = self.root.winfo_pointery() + 10
            self.show_nbt_tooltip(event, nbt_content, x, y)
        else:
            self.hide_nbt_tooltip()

    def on_treeview_leave(self, event):
        """处理鼠标离开Treeview事件"""
        self.hide_nbt_tooltip()
        self.reset_hover_bg()
        self.current_hover_item = None

    def reset_hover_bg(self):
        """重置悬停行背景色"""
        if self.current_hover_item:
            tags = [t for t in self.trade_listbox.item(self.current_hover_item, "tags") if t != "hover"]
            self.trade_listbox.item(self.current_hover_item, tags=tags)
            original_bg = self.original_bg.get(self.current_hover_item, "#ffffff")
            self.trade_listbox.tag_configure(tags[0], background=original_bg)

    # ---------------------- 指令生成与复制功能 ----------------------
    def generate_command(self):
        """生成指令并填充到选项卡"""
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
        
        # 填充到对应选项卡
        for i, (tab_name, _) in enumerate(self.tab_definitions):
            self._fill_cmd_to_tab(tab_name, commands[i])
        
        messagebox.showinfo("成功", "所有指令已生成！默认展示交易修改选项卡。\n如果是第一次创建，请按选项卡顺序执行命令")

    def _fill_cmd_to_tab(self, tab_name, command):
        """将指令填充到指定选项卡的文本框"""
        text_widget = self.command_tabs.get(tab_name)
        if not text_widget:
            return
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        text_widget.insert(1.0, command)
        text_widget.config(state=tk.DISABLED)

    def copy_command_to_clipboard(self, text_widget):
        """复制指令到剪贴板"""
        self.root.clipboard_clear()
        cmd_content = text_widget.get(1.0, tk.END).strip()
        if not cmd_content:
            messagebox.showwarning("提示", "当前选项卡无指令可复制！")
            return
        self.root.clipboard_append(cmd_content)
        messagebox.showinfo("成功", "指令已复制到剪贴板！")
