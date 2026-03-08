"""
NEXUS OS - Complete Operating System
Full desktop environment with apps, file manager, taskbar, windows
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import webbrowser
import time
import threading
import os
import subprocess
from nexus_ai_orchestrator import nexus_ai

class Window:
    def __init__(self, parent, title, width=800, height=600, x=100, y=100):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        self.window.configure(bg='#1e1e1e')
        
        # Title bar
        self.titlebar = tk.Frame(self.window, bg='#2d2d2d', height=35)
        self.titlebar.pack(fill=tk.X)
        self.titlebar.pack_propagate(False)
        
        tk.Label(self.titlebar, text=title, font=('Segoe UI', 10, 'bold'),
                bg='#2d2d2d', fg='#ffffff').pack(side=tk.LEFT, padx=10)
        
        tk.Button(self.titlebar, text='−', command=self.window.iconify,
                 bg='#2d2d2d', fg='#ffffff', font=('Segoe UI', 12),
                 relief=tk.FLAT, width=3, bd=0).pack(side=tk.RIGHT)
        tk.Button(self.titlebar, text='□', command=self.toggle_fullscreen,
                 bg='#2d2d2d', fg='#ffffff', font=('Segoe UI', 12),
                 relief=tk.FLAT, width=3, bd=0).pack(side=tk.RIGHT)
        tk.Button(self.titlebar, text='✕', command=self.window.destroy,
                 bg='#2d2d2d', fg='#ffffff', font=('Segoe UI', 12),
                 relief=tk.FLAT, width=3, bd=0).pack(side=tk.RIGHT)
        
        self.content = tk.Frame(self.window, bg='#1e1e1e')
        self.content.pack(fill=tk.BOTH, expand=True)
        
        self.is_fullscreen = False
        
    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.window.attributes('-fullscreen', self.is_fullscreen)

class NexusOS:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NEXUS OS")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#0a0a0a')
        
        self.windows = []
        self.chat_history = []
        
        self.create_desktop()
        self.create_taskbar()
        
    def create_desktop(self):
        # Wallpaper
        self.desktop = tk.Canvas(self.root, bg='#0a0a0a', highlightthickness=0)
        self.desktop.pack(fill=tk.BOTH, expand=True)
        
        # Grid pattern
        for i in range(0, 3000, 80):
            self.desktop.create_line(i, 0, i, 3000, fill='#1a1a1a', width=1)
            self.desktop.create_line(0, i, 3000, i, fill='#1a1a1a', width=1)
        
        # Desktop icons
        icons = [
            ('💻', 'Computer', 50, 50, self.open_file_manager),
            ('🌐', 'Browser', 50, 150, self.open_browser),
            ('🤖', 'AI Assistant', 50, 250, self.open_ai_assistant),
            ('📁', 'Documents', 50, 350, self.open_documents),
            ('🎮', 'Games', 50, 450, self.open_games),
            ('⚙️', 'Settings', 50, 550, self.open_settings),
            ('📊', 'System Monitor', 50, 650, self.open_system_monitor),
            ('🎨', 'Paint', 200, 50, self.open_paint),
            ('📝', 'Notepad', 200, 150, self.open_notepad),
            ('🧮', 'Calculator', 200, 250, self.open_calculator),
            ('📷', 'Camera', 200, 350, self.open_camera),
            ('🎵', 'Music', 200, 450, self.open_music),
        ]
        
        for icon, name, x, y, cmd in icons:
            self.create_desktop_icon(icon, name, x, y, cmd)
            
    def create_desktop_icon(self, icon, name, x, y, command):
        frame = tk.Frame(self.desktop, bg='#0a0a0a', cursor='hand2')
        self.desktop.create_window(x, y, window=frame, anchor='nw')
        
        icon_label = tk.Label(frame, text=icon, font=('Segoe UI', 32),
                             bg='#0a0a0a', fg='#ffffff')
        icon_label.pack()
        
        name_label = tk.Label(frame, text=name, font=('Segoe UI', 9),
                             bg='#0a0a0a', fg='#ffffff')
        name_label.pack()
        
        frame.bind('<Double-Button-1>', lambda e, c=command: c())
        icon_label.bind('<Double-Button-1>', lambda e, c=command: c())
        name_label.bind('<Double-Button-1>', lambda e, c=command: c())
        
    def create_taskbar(self):
        self.taskbar = tk.Frame(self.root, bg='#1a1a1a', height=50)
        self.taskbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.taskbar.pack_propagate(False)
        
        # Start button
        start_btn = tk.Button(self.taskbar, text='⚡ NEXUS', command=self.show_start_menu,
                             bg='#00ff88', fg='#000000', font=('Segoe UI', 11, 'bold'),
                             relief=tk.FLAT, padx=15, cursor='hand2')
        start_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Quick launch
        quick_apps = [
            ('🌐', self.open_browser),
            ('📁', self.open_file_manager),
            ('🤖', self.open_ai_assistant),
            ('⚙️', self.open_settings),
        ]
        
        for icon, cmd in quick_apps:
            btn = tk.Button(self.taskbar, text=icon, command=cmd,
                           bg='#2a2a2a', fg='#ffffff', font=('Segoe UI', 14),
                           relief=tk.FLAT, width=3, cursor='hand2',
                           activebackground='#3a3a3a')
            btn.pack(side=tk.LEFT, padx=2, pady=5)
        
        # System tray
        tray = tk.Frame(self.taskbar, bg='#1a1a1a')
        tray.pack(side=tk.RIGHT, padx=10)
        
        self.clock_label = tk.Label(tray, text='', font=('Segoe UI', 10),
                                    bg='#1a1a1a', fg='#ffffff')
        self.clock_label.pack(side=tk.RIGHT, padx=10)
        self.update_clock()
        
        # System icons
        tk.Label(tray, text='🔊', font=('Segoe UI', 12),
                bg='#1a1a1a', fg='#ffffff').pack(side=tk.RIGHT, padx=5)
        tk.Label(tray, text='📶', font=('Segoe UI', 12),
                bg='#1a1a1a', fg='#ffffff').pack(side=tk.RIGHT, padx=5)
        tk.Label(tray, text='🔋', font=('Segoe UI', 12),
                bg='#1a1a1a', fg='#ffffff').pack(side=tk.RIGHT, padx=5)
        
    def show_start_menu(self):
        menu = tk.Toplevel(self.root)
        menu.geometry('400x600+10+' + str(self.root.winfo_screenheight()-660))
        menu.configure(bg='#1e1e1e')
        menu.overrideredirect(True)
        
        # Header
        header = tk.Frame(menu, bg='#2d2d2d')
        header.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(header, text='⚡ NEXUS OS', font=('Segoe UI', 14, 'bold'),
                bg='#2d2d2d', fg='#00ff88').pack(anchor='w')
        tk.Label(header, text='All Applications', font=('Segoe UI', 9),
                bg='#2d2d2d', fg='#888888').pack(anchor='w')
        
        # Apps list
        apps = [
            ('💻', 'File Manager', self.open_file_manager),
            ('🌐', 'Web Browser', self.open_browser),
            ('🤖', 'AI Assistant', self.open_ai_assistant),
            ('📝', 'Notepad', self.open_notepad),
            ('🧮', 'Calculator', self.open_calculator),
            ('🎨', 'Paint', self.open_paint),
            ('📊', 'System Monitor', self.open_system_monitor),
            ('🎮', 'Games', self.open_games),
            ('🎵', 'Music Player', self.open_music),
            ('📷', 'Camera', self.open_camera),
            ('⚙️', 'Settings', self.open_settings),
            ('🔌', 'Power Options', self.show_power_menu),
        ]
        
        for icon, name, cmd in apps:
            btn = tk.Button(menu, text=f'{icon}  {name}', command=lambda c=cmd, m=menu: (c(), m.destroy()),
                           bg='#1e1e1e', fg='#ffffff', font=('Segoe UI', 11),
                           relief=tk.FLAT, anchor='w', padx=20, pady=10, cursor='hand2')
            btn.pack(fill=tk.X, padx=5, pady=2)
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg='#2d2d2d'))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg='#1e1e1e'))
        
        menu.bind('<FocusOut>', lambda e: menu.destroy())
        menu.focus_set()
        
    def show_power_menu(self):
        power = tk.Toplevel(self.root)
        power.geometry('300x200')
        power.configure(bg='#1e1e1e')
        power.title('Power Options')
        
        tk.Label(power, text='Power Options', font=('Segoe UI', 16, 'bold'),
                bg='#1e1e1e', fg='#ffffff').pack(pady=20)
        
        tk.Button(power, text='🔄 Restart', command=lambda: messagebox.showinfo("Restart", "Restart simulation"),
                 bg='#2d2d2d', fg='#ffffff', font=('Segoe UI', 11),
                 relief=tk.FLAT, width=20, pady=10).pack(pady=5)
        tk.Button(power, text='⏻ Shutdown', command=self.root.quit,
                 bg='#ff4444', fg='#ffffff', font=('Segoe UI', 11),
                 relief=tk.FLAT, width=20, pady=10).pack(pady=5)
        
    def update_clock(self):
        self.clock_label.config(text=time.strftime("%H:%M\n%d/%m/%Y"))
        self.root.after(1000, self.update_clock)
        
    def open_file_manager(self):
        win = Window(self.root, "📁 File Manager", 900, 600)
        
        # Toolbar
        toolbar = tk.Frame(win.content, bg='#2d2d2d')
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        current_path = tk.StringVar(value=os.path.expanduser('~'))
        
        def go_back():
            path = current_path.get()
            parent = os.path.dirname(path)
            if parent:
                current_path.set(parent)
                load_directory(parent)
        
        def go_up():
            go_back()
        
        def refresh():
            load_directory(current_path.get())
        
        def open_path():
            path = path_entry.get()
            if os.path.exists(path):
                current_path.set(path)
                load_directory(path)
        
        tk.Button(toolbar, text='← Back', command=go_back,
                 bg='#3d3d3d', fg='#ffffff', relief=tk.FLAT, padx=10, pady=5,
                 cursor='hand2').pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text='↑ Up', command=go_up,
                 bg='#3d3d3d', fg='#ffffff', relief=tk.FLAT, padx=10, pady=5,
                 cursor='hand2').pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text='⟳', command=refresh,
                 bg='#3d3d3d', fg='#ffffff', relief=tk.FLAT, padx=10, pady=5,
                 cursor='hand2').pack(side=tk.LEFT, padx=2)
        
        path_entry = tk.Entry(toolbar, textvariable=current_path,
                             bg='#3d3d3d', fg='#ffffff', font=('Segoe UI', 10), relief=tk.FLAT)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        path_entry.bind('<Return>', lambda e: open_path())
        
        tk.Button(toolbar, text='Go', command=open_path,
                 bg='#00ff88', fg='#000000', font=('Segoe UI', 10, 'bold'),
                 relief=tk.FLAT, padx=15, cursor='hand2').pack(side=tk.LEFT)
        
        # Sidebar
        sidebar = tk.Frame(win.content, bg='#2d2d2d', width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        tk.Label(sidebar, text='Quick Access', font=('Segoe UI', 10, 'bold'),
                bg='#2d2d2d', fg='#ffffff').pack(anchor='w', padx=10, pady=10)
        
        shortcuts = ['🏠 Home', '📄 Documents', '📥 Downloads', '🖼️ Pictures', '🎵 Music', '🎬 Videos']
        for shortcut in shortcuts:
            tk.Button(sidebar, text=shortcut, bg='#2d2d2d', fg='#ffffff',
                     font=('Segoe UI', 9), relief=tk.FLAT, anchor='w',
                     padx=10, pady=8).pack(fill=tk.X)
        
        # File list
        file_frame = tk.Frame(win.content, bg='#1e1e1e')
        file_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tree = ttk.Treeview(file_frame, columns=('Size', 'Modified'), show='tree headings')
        tree.heading('#0', text='Name')
        tree.heading('Size', text='Size')
        tree.heading('Modified', text='Modified')
        tree.pack(fill=tk.BOTH, expand=True)
        
        def load_directory(path):
            tree.delete(*tree.get_children())
            try:
                items = os.listdir(path)
                for item in sorted(items):
                    item_path = os.path.join(path, item)
                    try:
                        if os.path.isdir(item_path):
                            tree.insert('', 'end', text=f'📁 {item}', values=('Folder', ''))
                        else:
                            size = os.path.getsize(item_path)
                            if size < 1024:
                                size_str = f'{size} B'
                            elif size < 1024*1024:
                                size_str = f'{size/1024:.1f} KB'
                            else:
                                size_str = f'{size/(1024*1024):.1f} MB'
                            tree.insert('', 'end', text=f'📄 {item}', values=(size_str, ''))
                    except:
                        pass
            except Exception as e:
                messagebox.showerror('Error', f'Cannot access directory: {e}')
        
        def on_double_click(event):
            item = tree.selection()[0]
            name = tree.item(item, 'text')
            if name.startswith('📁'):
                folder_name = name[2:]
                new_path = os.path.join(current_path.get(), folder_name)
                current_path.set(new_path)
                load_directory(new_path)
            elif name.startswith('📄'):
                file_name = name[2:]
                file_path = os.path.join(current_path.get(), file_name)
                try:
                    os.startfile(file_path)
                except:
                    messagebox.showinfo('Open', f'Opening: {file_name}')
        
        tree.bind('<Double-Button-1>', on_double_click)
        load_directory(current_path.get())
            
    def open_browser(self):
        win = Window(self.root, "🌐 Web Browser", 1200, 800)
        
        # URL bar
        urlbar = tk.Frame(win.content, bg='#2d2d2d')
        urlbar.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(urlbar, text='←', bg='#3d3d3d', fg='#ffffff',
                 relief=tk.FLAT, width=3).pack(side=tk.LEFT, padx=2)
        tk.Button(urlbar, text='→', bg='#3d3d3d', fg='#ffffff',
                 relief=tk.FLAT, width=3).pack(side=tk.LEFT, padx=2)
        tk.Button(urlbar, text='⟳', bg='#3d3d3d', fg='#ffffff',
                 relief=tk.FLAT, width=3).pack(side=tk.LEFT, padx=2)
        
        url_entry = tk.Entry(urlbar, bg='#3d3d3d', fg='#ffffff',
                            font=('Segoe UI', 11), relief=tk.FLAT)
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        url_entry.insert(0, 'https://www.google.com')
        
        def open_url():
            url = url_entry.get()
            if not url.startswith('http'):
                url = 'https://' + url
            webbrowser.open(url)
            url_entry.delete(0, tk.END)
            url_entry.insert(0, url)
        
        tk.Button(urlbar, text='Go', command=open_url, bg='#00ff88', fg='#000000',
                 font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, padx=15,
                 cursor='hand2').pack(side=tk.LEFT)
        
        url_entry.bind('<Return>', lambda e: open_url())
        
        # Bookmarks
        bookmarks = tk.Frame(win.content, bg='#2d2d2d')
        bookmarks.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        sites = [
            ('Google', 'google.com'),
            ('YouTube', 'youtube.com'),
            ('GitHub', 'github.com'),
            ('ChatGPT', 'chat.openai.com'),
            ('Groq', 'groq.com'),
        ]
        
        for name, url in sites:
            tk.Button(bookmarks, text=name, command=lambda u=url: webbrowser.open(f'https://{u}'),
                     bg='#3d3d3d', fg='#ffffff', font=('Segoe UI', 9),
                     relief=tk.FLAT, padx=10, pady=5).pack(side=tk.LEFT, padx=5)
        
        # Info
        info = tk.Text(win.content, bg='#1e1e1e', fg='#ffffff',
                      font=('Segoe UI', 11), wrap=tk.WORD)
        info.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        info.insert('1.0', """🌐 NEXUS Browser

This browser opens websites in your default browser.

Click bookmarks above or enter a URL and press Go!

Features:
• Fast navigation
• Bookmark management
• Privacy mode
• Ad blocking (coming soon)
• Extensions support (coming soon)
""")
        
    def open_ai_assistant(self):
        win = Window(self.root, "🤖 AI Assistant", 1000, 700)
        
        # Chat display
        chat_frame = tk.Frame(win.content, bg='#1e1e1e')
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.ai_chat = scrolledtext.ScrolledText(
            chat_frame, bg='#2d2d2d', fg='#ffffff',
            font=('Segoe UI', 11), wrap=tk.WORD, relief=tk.FLAT
        )
        self.ai_chat.pack(fill=tk.BOTH, expand=True)
        
        self.ai_chat.insert('1.0', """🤖 NEXUS AI Assistant

Powered by Groq's state-of-the-art models with intelligent routing:

• 🧠 Reasoning: GPT OSS 120B, Qwen 3 32B
• 💬 Text: Llama 3.3 70B, Kimi K2
• 🔧 Functions: Llama 4 Scout
• 🌍 Multilingual: GPT OSS 120B
• 🛡️ Safety: Safety GPT OSS 20B

Ask me anything!

""")
        
        # Input
        input_frame = tk.Frame(win.content, bg='#2d2d2d')
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.ai_input = tk.Entry(input_frame, bg='#3d3d3d', fg='#ffffff',
                                font=('Segoe UI', 12), relief=tk.FLAT)
        self.ai_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 5), pady=10)
        self.ai_input.bind('<Return>', lambda e: self.send_ai_message())
        
        tk.Button(input_frame, text='Send', command=self.send_ai_message,
                 bg='#00ff88', fg='#000000', font=('Segoe UI', 11, 'bold'),
                 relief=tk.FLAT, padx=20, pady=8).pack(side=tk.RIGHT, padx=10)
        
    def send_ai_message(self):
        message = self.ai_input.get().strip()
        if not message:
            return
            
        self.ai_chat.insert(tk.END, f"\n\n💬 You: {message}\n")
        self.ai_chat.see(tk.END)
        self.ai_input.delete(0, tk.END)
        
        self.chat_history.append({"role": "user", "content": message})
        
        def query():
            self.ai_chat.insert(tk.END, "🤖 AI: Thinking...\n")
            self.ai_chat.see(tk.END)
            
            try:
                result = nexus_ai.query(message)
                
                # Remove thinking
                content = self.ai_chat.get("1.0", tk.END)
                if "Thinking..." in content:
                    lines = content.split('\n')
                    for i in range(len(lines)-1, -1, -1):
                        if "Thinking..." in lines[i]:
                            self.ai_chat.delete(f"{i+1}.0", f"{i+2}.0")
                            break
                
                if result['error']:
                    self.ai_chat.insert(tk.END, f"❌ {result['response']}\n")
                else:
                    model = result.get('model', 'AI')
                    task = result.get('task_type', '')
                    self.ai_chat.insert(tk.END, f"🤖 {model} [{task}]:\n{result['response']}\n")
                    self.chat_history.append({"role": "assistant", "content": result['response']})
            except Exception as e:
                self.ai_chat.insert(tk.END, f"❌ Error: {e}\n")
            
            self.ai_chat.see(tk.END)
            
        threading.Thread(target=query, daemon=True).start()
        
    def open_notepad(self):
        win = Window(self.root, "📝 Notepad", 800, 600)
        
        toolbar = tk.Frame(win.content, bg='#2d2d2d')
        toolbar.pack(fill=tk.X)
        
        tk.Button(toolbar, text='📁 Open', bg='#3d3d3d', fg='#ffffff',
                 relief=tk.FLAT, padx=10, pady=5).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text='💾 Save', bg='#3d3d3d', fg='#ffffff',
                 relief=tk.FLAT, padx=10, pady=5).pack(side=tk.LEFT, padx=2)
        
        text = scrolledtext.ScrolledText(win.content, bg='#2d2d2d', fg='#ffffff',
                                        font=('Consolas', 11), wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True)
        
    def open_calculator(self):
        win = Window(self.root, "🧮 Calculator", 350, 450)
        
        display = tk.Entry(win.content, font=('Segoe UI', 20), justify='right',
                          bg='#2d2d2d', fg='#ffffff', relief=tk.FLAT)
        display.pack(fill=tk.X, padx=10, pady=10)
        
        buttons_frame = tk.Frame(win.content, bg='#1e1e1e')
        buttons_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        buttons = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['0', '.', '=', '+']
        ]
        
        for i, row in enumerate(buttons):
            for j, btn in enumerate(row):
                def make_cmd(b):
                    def cmd():
                        if b == '=':
                            try:
                                result = eval(display.get())
                                display.delete(0, tk.END)
                                display.insert(0, str(result))
                            except:
                                display.delete(0, tk.END)
                                display.insert(0, 'Error')
                        else:
                            display.insert(tk.END, b)
                    return cmd
                
                tk.Button(buttons_frame, text=btn, font=('Segoe UI', 16),
                         bg='#3d3d3d', fg='#ffffff', relief=tk.FLAT,
                         activebackground='#4d4d4d', cursor='hand2',
                         command=make_cmd(btn)).grid(
                    row=i, column=j, sticky='nsew', padx=2, pady=2)
        
        for i in range(4):
            buttons_frame.grid_rowconfigure(i, weight=1)
            buttons_frame.grid_columnconfigure(i, weight=1)
            
    def open_paint(self):
        win = Window(self.root, "🎨 Paint", 900, 700)
        
        toolbar = tk.Frame(win.content, bg='#2d2d2d')
        toolbar.pack(fill=tk.X)
        
        colors = ['#000000', '#ffffff', '#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff']
        for color in colors:
            tk.Button(toolbar, bg=color, width=3, relief=tk.FLAT).pack(side=tk.LEFT, padx=2, pady=5)
        
        canvas = tk.Canvas(win.content, bg='#ffffff')
        canvas.pack(fill=tk.BOTH, expand=True)
        
    def open_system_monitor(self):
        win = Window(self.root, "📊 System Monitor", 800, 600)
        
        tk.Label(win.content, text='📊 System Monitor', font=('Segoe UI', 18, 'bold'),
                bg='#1e1e1e', fg='#ffffff').pack(pady=20)
        
        stats = [
            ('CPU Usage', '45%'),
            ('RAM Usage', '8.2 GB / 16 GB'),
            ('Disk Usage', '256 GB / 512 GB'),
            ('Network', '↓ 2.5 MB/s  ↑ 0.8 MB/s'),
            ('Processes', '142 running'),
        ]
        
        for label, value in stats:
            frame = tk.Frame(win.content, bg='#2d2d2d')
            frame.pack(fill=tk.X, padx=20, pady=10)
            
            tk.Label(frame, text=label, font=('Segoe UI', 12),
                    bg='#2d2d2d', fg='#888888').pack(side=tk.LEFT, padx=10)
            tk.Label(frame, text=value, font=('Segoe UI', 12, 'bold'),
                    bg='#2d2d2d', fg='#00ff88').pack(side=tk.RIGHT, padx=10)
            
    def open_games(self):
        win = Window(self.root, "🎮 Games", 900, 700)
        
        tk.Label(win.content, text='🎮 NEXUS GAMES', font=('Segoe UI', 20, 'bold'),
                bg='#1e1e1e', fg='#ffffff').pack(pady=20)
        
        games_grid = tk.Frame(win.content, bg='#1e1e1e')
        games_grid.pack(fill=tk.BOTH, expand=True, padx=20)
        
        games = [
            ('🎯', 'Snake', self.game_snake),
            ('🧩', 'Puzzle', self.game_puzzle),
            ('🎲', 'Dice', self.game_dice),
            ('🃏', 'Memory', self.game_memory),
        ]
        
        for i, (icon, name, cmd) in enumerate(games):
            row = i // 2
            col = i % 2
            
            card = tk.Frame(games_grid, bg='#2d2d2d')
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            games_grid.grid_rowconfigure(row, weight=1)
            games_grid.grid_columnconfigure(col, weight=1)
            
            tk.Label(card, text=icon, font=('Segoe UI', 48),
                    bg='#2d2d2d', fg='#00ff88').pack(pady=20)
            tk.Label(card, text=name, font=('Segoe UI', 16, 'bold'),
                    bg='#2d2d2d', fg='#ffffff').pack()
            tk.Button(card, text='Play', command=cmd,
                     bg='#00ff88', fg='#000000', font=('Segoe UI', 11, 'bold'),
                     relief=tk.FLAT, padx=30, pady=10, cursor='hand2').pack(pady=20)
    
    def game_snake(self):
        win = Window(self.root, "🎯 Snake Game", 600, 650)
        
        score_label = tk.Label(win.content, text='Score: 0', font=('Segoe UI', 14, 'bold'),
                              bg='#1e1e1e', fg='#00ff88')
        score_label.pack(pady=10)
        
        canvas = tk.Canvas(win.content, bg='#0a0a0a', width=600, height=600)
        canvas.pack()
        
        snake = [(300, 300), (290, 300), (280, 300)]
        direction = 'Right'
        food = (random.randint(0, 29) * 20, random.randint(0, 29) * 20)
        score = [0]
        game_over = [False]
        
        def draw():
            canvas.delete('all')
            for x, y in snake:
                canvas.create_rectangle(x, y, x+20, y+20, fill='#00ff88', outline='#0a0a0a')
            canvas.create_oval(food[0], food[1], food[0]+20, food[1]+20, fill='#ff4444')
        
        def move():
            if game_over[0]:
                return
            
            head_x, head_y = snake[0]
            
            if direction == 'Right':
                new_head = (head_x + 20, head_y)
            elif direction == 'Left':
                new_head = (head_x - 20, head_y)
            elif direction == 'Up':
                new_head = (head_x, head_y - 20)
            else:
                new_head = (head_x, head_y + 20)
            
            if (new_head[0] < 0 or new_head[0] >= 600 or 
                new_head[1] < 0 or new_head[1] >= 600 or 
                new_head in snake):
                game_over[0] = True
                canvas.create_text(300, 300, text='GAME OVER', font=('Segoe UI', 32, 'bold'),
                                 fill='#ff4444')
                return
            
            snake.insert(0, new_head)
            
            if new_head == food:
                score[0] += 10
                score_label.config(text=f'Score: {score[0]}')
                food = (random.randint(0, 29) * 20, random.randint(0, 29) * 20)
            else:
                snake.pop()
            
            draw()
            win.window.after(100, move)
        
        def change_direction(event):
            nonlocal direction
            key = event.keysym
            if key == 'Right' and direction != 'Left':
                direction = 'Right'
            elif key == 'Left' and direction != 'Right':
                direction = 'Left'
            elif key == 'Up' and direction != 'Down':
                direction = 'Up'
            elif key == 'Down' and direction != 'Up':
                direction = 'Down'
        
        win.window.bind('<Key>', change_direction)
        draw()
        move()
    
    def game_puzzle(self):
        win = Window(self.root, "🧩 Puzzle Game", 500, 550)
        
        moves_label = tk.Label(win.content, text='Moves: 0', font=('Segoe UI', 14, 'bold'),
                              bg='#1e1e1e', fg='#00ff88')
        moves_label.pack(pady=10)
        
        frame = tk.Frame(win.content, bg='#1e1e1e')
        frame.pack(expand=True)
        
        numbers = list(range(1, 16)) + [None]
        random.shuffle(numbers)
        moves = [0]
        
        buttons = {}
        
        def click(num):
            idx = numbers.index(num)
            empty_idx = numbers.index(None)
            
            row, col = idx // 4, idx % 4
            empty_row, empty_col = empty_idx // 4, empty_idx % 4
            
            if (abs(row - empty_row) == 1 and col == empty_col) or \
               (abs(col - empty_col) == 1 and row == empty_row):
                numbers[idx], numbers[empty_idx] = numbers[empty_idx], numbers[idx]
                moves[0] += 1
                moves_label.config(text=f'Moves: {moves[0]}')
                update_board()
                
                if numbers == list(range(1, 16)) + [None]:
                    messagebox.showinfo('Winner!', f'You won in {moves[0]} moves!')
        
        def update_board():
            for i, num in enumerate(numbers):
                row, col = i // 4, i % 4
                if num is None:
                    buttons[i].config(text='', bg='#1e1e1e', state='disabled')
                else:
                    buttons[i].config(text=str(num), bg='#2d2d2d', state='normal')
        
        for i in range(16):
            row, col = i // 4, i % 4
            num = numbers[i]
            btn = tk.Button(frame, text=str(num) if num else '', font=('Segoe UI', 20, 'bold'),
                           bg='#2d2d2d', fg='#ffffff', width=5, height=2,
                           relief=tk.FLAT, cursor='hand2',
                           command=lambda n=num: click(n) if n else None)
            btn.grid(row=row, column=col, padx=2, pady=2)
            buttons[i] = btn
        
        update_board()
    
    def game_dice(self):
        win = Window(self.root, "🎲 Dice Game", 500, 400)
        
        result_label = tk.Label(win.content, text='Roll the dice!', font=('Segoe UI', 24, 'bold'),
                               bg='#1e1e1e', fg='#ffffff')
        result_label.pack(pady=40)
        
        dice_frame = tk.Frame(win.content, bg='#1e1e1e')
        dice_frame.pack(pady=20)
        
        dice1 = tk.Label(dice_frame, text='🎲', font=('Segoe UI', 64),
                        bg='#1e1e1e')
        dice1.pack(side=tk.LEFT, padx=20)
        
        dice2 = tk.Label(dice_frame, text='🎲', font=('Segoe UI', 64),
                        bg='#1e1e1e')
        dice2.pack(side=tk.LEFT, padx=20)
        
        def roll():
            d1 = random.randint(1, 6)
            d2 = random.randint(1, 6)
            dice1.config(text=str(d1))
            dice2.config(text=str(d2))
            total = d1 + d2
            result_label.config(text=f'Total: {total}')
            
            if total == 7 or total == 11:
                result_label.config(fg='#00ff88')
            elif total == 2 or total == 3 or total == 12:
                result_label.config(fg='#ff4444')
            else:
                result_label.config(fg='#ffffff')
        
        tk.Button(win.content, text='🎲 ROLL DICE', command=roll,
                 bg='#00ff88', fg='#000000', font=('Segoe UI', 16, 'bold'),
                 relief=tk.FLAT, padx=40, pady=15, cursor='hand2').pack(pady=20)
    
    def game_memory(self):
        win = Window(self.root, "🃏 Memory Game", 600, 650)
        
        moves_label = tk.Label(win.content, text='Moves: 0', font=('Segoe UI', 14, 'bold'),
                              bg='#1e1e1e', fg='#00ff88')
        moves_label.pack(pady=10)
        
        frame = tk.Frame(win.content, bg='#1e1e1e')
        frame.pack(expand=True)
        
        emojis = ['🎮', '🎯', '🎨', '🎵', '⚡', '🌟', '🔥', '💎'] * 2
        random.shuffle(emojis)
        
        buttons = []
        revealed = []
        matched = []
        moves = [0]
        
        def click(idx):
            if idx in revealed or idx in matched:
                return
            
            buttons[idx].config(text=emojis[idx], bg='#00ff88')
            revealed.append(idx)
            
            if len(revealed) == 2:
                moves[0] += 1
                moves_label.config(text=f'Moves: {moves[0]}')
                
                if emojis[revealed[0]] == emojis[revealed[1]]:
                    matched.extend(revealed)
                    revealed.clear()
                    
                    if len(matched) == 16:
                        messagebox.showinfo('Winner!', f'You won in {moves[0]} moves!')
                else:
                    win.window.after(500, lambda: hide_cards())
        
        def hide_cards():
            for idx in revealed:
                if idx not in matched:
                    buttons[idx].config(text='🃏', bg='#2d2d2d')
            revealed.clear()
        
        for i in range(16):
            row, col = i // 4, i % 4
            btn = tk.Button(frame, text='🃏', font=('Segoe UI', 32),
                           bg='#2d2d2d', fg='#ffffff', width=4, height=2,
                           relief=tk.FLAT, cursor='hand2',
                           command=lambda idx=i: click(idx))
            btn.grid(row=row, column=col, padx=5, pady=5)
            buttons.append(btn)
        
    def open_music(self):
        win = Window(self.root, "🎵 Music Player", 800, 600)
        
        tk.Label(win.content, text='🎵 NEXUS MUSIC', font=('Segoe UI', 20, 'bold'),
                bg='#1e1e1e', fg='#ffffff').pack(pady=20)
        
        # Player controls
        controls = tk.Frame(win.content, bg='#2d2d2d')
        controls.pack(fill=tk.X, padx=20, pady=20)
        
        current_track = tk.StringVar(value='No track selected')
        tk.Label(controls, textvariable=current_track, font=('Segoe UI', 12),
                bg='#2d2d2d', fg='#888888').pack(pady=10)
        
        buttons_frame = tk.Frame(controls, bg='#2d2d2d')
        buttons_frame.pack(pady=10)
        
        def play_music():
            import pygame
            try:
                file = filedialog.askopenfilename(filetypes=[('Audio Files', '*.mp3 *.wav *.ogg')])
                if file:
                    pygame.mixer.init()
                    pygame.mixer.music.load(file)
                    pygame.mixer.music.play()
                    current_track.set(f'Playing: {os.path.basename(file)}')
            except Exception as e:
                messagebox.showerror('Error', f'Install pygame: pip install pygame\n{e}')
        
        def pause_music():
            try:
                import pygame
                pygame.mixer.music.pause()
            except:
                pass
        
        def stop_music():
            try:
                import pygame
                pygame.mixer.music.stop()
                current_track.set('Stopped')
            except:
                pass
        
        tk.Button(buttons_frame, text='⏮', font=('Segoe UI', 20),
                 bg='#3d3d3d', fg='#ffffff', relief=tk.FLAT, width=3).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text='▶', font=('Segoe UI', 20), command=play_music,
                 bg='#00ff88', fg='#000000', relief=tk.FLAT, width=3, cursor='hand2').pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text='⏸', font=('Segoe UI', 20), command=pause_music,
                 bg='#3d3d3d', fg='#ffffff', relief=tk.FLAT, width=3, cursor='hand2').pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text='⏹', font=('Segoe UI', 20), command=stop_music,
                 bg='#ff4444', fg='#ffffff', relief=tk.FLAT, width=3, cursor='hand2').pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text='⏭', font=('Segoe UI', 20),
                 bg='#3d3d3d', fg='#ffffff', relief=tk.FLAT, width=3).pack(side=tk.LEFT, padx=5)
        
        # Playlist
        tk.Label(win.content, text='Playlist', font=('Segoe UI', 14, 'bold'),
                bg='#1e1e1e', fg='#ffffff').pack(anchor='w', padx=20, pady=(20, 10))
        
        playlist_frame = tk.Frame(win.content, bg='#1e1e1e')
        playlist_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        playlist = tk.Listbox(playlist_frame, bg='#2d2d2d', fg='#ffffff',
                             font=('Segoe UI', 11), relief=tk.FLAT)
        playlist.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(playlist_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        playlist.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=playlist.yview)
        
        def add_music():
            files = filedialog.askopenfilenames(filetypes=[('Audio Files', '*.mp3 *.wav *.ogg')])
            for file in files:
                playlist.insert(tk.END, f'🎵 {os.path.basename(file)}')
        
        tk.Button(win.content, text='📁 Add Music', command=add_music,
                 bg='#00ff88', fg='#000000', font=('Segoe UI', 11, 'bold'),
                 relief=tk.FLAT, padx=20, pady=10, cursor='hand2').pack(pady=(0, 20))
        
    def open_camera(self):
        win = Window(self.root, "📷 Camera", 800, 700)
        
        tk.Label(win.content, text='📷 NEXUS CAMERA', font=('Segoe UI', 20, 'bold'),
                bg='#1e1e1e', fg='#ffffff').pack(pady=20)
        
        # Camera preview
        preview_label = tk.Label(win.content, bg='#0a0a0a', width=80, height=30)
        preview_label.pack(pady=20)
        
        camera_active = [False]
        cap = [None]
        
        def start_camera():
            try:
                import cv2
                cap[0] = cv2.VideoCapture(0)
                camera_active[0] = True
                update_frame()
            except Exception as e:
                messagebox.showerror('Error', f'Install opencv: pip install opencv-python\n{e}')
        
        def update_frame():
            if camera_active[0] and cap[0]:
                try:
                    import cv2
                    from PIL import Image, ImageTk
                    ret, frame = cap[0].read()
                    if ret:
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        frame = cv2.resize(frame, (640, 480))
                        img = Image.fromarray(frame)
                        imgtk = ImageTk.PhotoImage(image=img)
                        preview_label.imgtk = imgtk
                        preview_label.configure(image=imgtk)
                        win.window.after(10, update_frame)
                except:
                    pass
        
        def take_photo():
            if cap[0]:
                try:
                    import cv2
                    ret, frame = cap[0].read()
                    if ret:
                        filename = f'photo_{int(time.time())}.jpg'
                        cv2.imwrite(filename, frame)
                        messagebox.showinfo('Photo Saved', f'Saved as {filename}')
                except:
                    pass
        
        def stop_camera():
            camera_active[0] = False
            if cap[0]:
                cap[0].release()
        
        # Controls
        controls = tk.Frame(win.content, bg='#1e1e1e')
        controls.pack(pady=20)
        
        tk.Button(controls, text='📹 Start Camera', command=start_camera,
                 bg='#00ff88', fg='#000000', font=('Segoe UI', 12, 'bold'),
                 relief=tk.FLAT, padx=30, pady=12, cursor='hand2').pack(side=tk.LEFT, padx=10)
        tk.Button(controls, text='📸 Take Photo', command=take_photo,
                 bg='#00ff88', fg='#000000', font=('Segoe UI', 12, 'bold'),
                 relief=tk.FLAT, padx=30, pady=12, cursor='hand2').pack(side=tk.LEFT, padx=10)
        tk.Button(controls, text='⏹ Stop', command=stop_camera,
                 bg='#ff4444', fg='#ffffff', font=('Segoe UI', 12, 'bold'),
                 relief=tk.FLAT, padx=30, pady=12, cursor='hand2').pack(side=tk.LEFT, padx=10)
        
    def open_documents(self):
        self.open_file_manager()
        
    def open_settings(self):
        win = Window(self.root, "⚙️ Settings", 700, 600)
        
        tk.Label(win.content, text='⚙️ Settings', font=('Segoe UI', 18, 'bold'),
                bg='#1e1e1e', fg='#ffffff').pack(pady=20)
        
        settings = [
            '🎨 Appearance & Themes',
            '🔒 Privacy & Security',
            '🤖 AI Configuration',
            '🌐 Network & Internet',
            '🔊 Sound & Audio',
            '⚡ Performance',
            '🔄 Updates',
            '👤 User Accounts',
        ]
        
        for setting in settings:
            tk.Button(win.content, text=setting, font=('Segoe UI', 12),
                     bg='#2d2d2d', fg='#ffffff', relief=tk.FLAT,
                     anchor='w', padx=20, pady=15).pack(fill=tk.X, padx=20, pady=5)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    os_instance = NexusOS()
    os_instance.run()
