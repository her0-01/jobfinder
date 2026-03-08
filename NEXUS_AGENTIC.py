"""
NEXUS AGENTIC AI - Revolutionary Multi-Agent System
Visual workflow builder with autonomous AI agents
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import threading
import time
import requests
from datetime import datetime

class AIAgent:
    def __init__(self, name, model, api_key, specialty):
        self.name = name
        self.model = model
        self.api_key = api_key
        self.specialty = specialty
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        
    def execute(self, task, context=""):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"{context}\n\nTask: {task}" if context else task
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2048
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "result": result['choices'][0]['message']['content'],
                    "agent": self.name,
                    "model": self.model
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

class WorkflowNode:
    def __init__(self, node_id, node_type, agent, task, x, y):
        self.id = node_id
        self.type = node_type  # 'start', 'agent', 'decision', 'merge', 'end'
        self.agent = agent
        self.task = task
        self.x = x
        self.y = y
        self.connections = []
        self.result = None

class NexusAgenticAI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NEXUS AGENTIC AI - Revolutionary Multi-Agent System")
        self.root.geometry("1600x900")
        self.root.configure(bg='#0a0a0a')
        
        self.api_key = os.getenv('GROQ_API_KEY', 'YOUR_API_KEY_HERE')
        
        # Initialize AI Agents
        self.agents = {
            'Researcher': AIAgent('Researcher', 'llama-3.3-70b-versatile', self.api_key, 'Research & Analysis'),
            'Writer': AIAgent('Writer', 'llama-3.1-8b-instant', self.api_key, 'Content Creation'),
            'Coder': AIAgent('Coder', 'llama-3.3-70b-versatile', self.api_key, 'Code Generation'),
            'Analyst': AIAgent('Analyst', 'gemma2-9b-it', self.api_key, 'Data Analysis'),
            'Strategist': AIAgent('Strategist', 'llama-3.3-70b-versatile', self.api_key, 'Strategy & Planning'),
            'Critic': AIAgent('Critic', 'llama-3.1-8b-instant', self.api_key, 'Quality Review'),
        }
        
        self.workflows = {}
        self.current_workflow = []
        self.workflow_results = []
        self.node_counter = 0
        
        self.create_ui()
        
    def create_ui(self):
        # Top bar
        topbar = tk.Frame(self.root, bg='#1a1a1a', height=60)
        topbar.pack(side=tk.TOP, fill=tk.X)
        
        tk.Label(topbar, text="⚡ NEXUS AGENTIC AI", font=('Segoe UI', 18, 'bold'),
                bg='#1a1a1a', fg='#00ff88').pack(side=tk.LEFT, padx=20)
        
        tk.Label(topbar, text="Revolutionary Multi-Agent Workflow System", font=('Segoe UI', 10),
                bg='#1a1a1a', fg='#888888').pack(side=tk.LEFT)
        
        tk.Button(topbar, text='✕ Exit', command=self.root.quit,
                 bg='#ff4444', fg='white', font=('Segoe UI', 10, 'bold'),
                 relief=tk.FLAT, padx=15, pady=8).pack(side=tk.RIGHT, padx=10)
        
        # Main container
        main = tk.Frame(self.root, bg='#0a0a0a')
        main.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Workflow Builder
        left_panel = tk.Frame(main, bg='#1a1a1a', width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False)
        
        tk.Label(left_panel, text="🔧 WORKFLOW BUILDER", font=('Segoe UI', 14, 'bold'),
                bg='#1a1a1a', fg='#ffffff').pack(pady=20)
        
        # Agent selection
        tk.Label(left_panel, text="Select Agents:", font=('Segoe UI', 11, 'bold'),
                bg='#1a1a1a', fg='#00ff88').pack(anchor='w', padx=20, pady=(10, 5))
        
        self.agent_vars = {}
        for agent_name, agent in self.agents.items():
            var = tk.BooleanVar(value=True)
            self.agent_vars[agent_name] = var
            
            frame = tk.Frame(left_panel, bg='#2a2a2a')
            frame.pack(fill=tk.X, padx=20, pady=3)
            
            tk.Checkbutton(frame, text=f"{agent_name} - {agent.specialty}",
                          variable=var, bg='#2a2a2a', fg='#ffffff',
                          font=('Segoe UI', 10), selectcolor='#1a1a1a',
                          activebackground='#2a2a2a').pack(anchor='w', padx=10, pady=8)
        
        # Workflow modes
        tk.Label(left_panel, text="Workflow Mode:", font=('Segoe UI', 11, 'bold'),
                bg='#1a1a1a', fg='#00ff88').pack(anchor='w', padx=20, pady=(20, 5))
        
        self.workflow_mode = tk.StringVar(value='sequential')
        
        modes = [
            ('sequential', '📋 Sequential', 'Agents work one after another'),
            ('parallel', '⚡ Parallel', 'All agents work simultaneously'),
            ('debate', '💬 Debate', 'Agents discuss and refine'),
            ('hierarchical', '🏢 Hierarchical', 'Manager coordinates agents'),
            ('autonomous', '🤖 Autonomous', 'Agents self-organize'),
        ]
        
        for value, label, desc in modes:
            frame = tk.Frame(left_panel, bg='#2a2a2a')
            frame.pack(fill=tk.X, padx=20, pady=3)
            
            rb = tk.Radiobutton(frame, text=label, variable=self.workflow_mode,
                               value=value, bg='#2a2a2a', fg='#ffffff',
                               font=('Segoe UI', 10, 'bold'), selectcolor='#1a1a1a',
                               activebackground='#2a2a2a')
            rb.pack(anchor='w', padx=10, pady=5)
            
            tk.Label(frame, text=desc, font=('Segoe UI', 8),
                    bg='#2a2a2a', fg='#888888').pack(anchor='w', padx=30)
        
        # Task input
        tk.Label(left_panel, text="Task Description:", font=('Segoe UI', 11, 'bold'),
                bg='#1a1a1a', fg='#00ff88').pack(anchor='w', padx=20, pady=(20, 5))
        
        self.task_input = tk.Text(left_panel, bg='#2a2a2a', fg='#ffffff',
                                 font=('Segoe UI', 10), wrap=tk.WORD, height=6,
                                 relief=tk.FLAT)
        self.task_input.pack(fill=tk.X, padx=20, pady=5)
        self.task_input.insert('1.0', 'Create a comprehensive business plan for a SaaS startup...')
        
        # Execute button
        tk.Button(left_panel, text='🚀 EXECUTE WORKFLOW', command=self.execute_workflow,
                 bg='#00ff88', fg='#000000', font=('Segoe UI', 12, 'bold'),
                 relief=tk.FLAT, pady=15, cursor='hand2').pack(fill=tk.X, padx=20, pady=20)
        
        # Right panel - Results & Visualization
        right_panel = tk.Frame(main, bg='#0a0a0a')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Tabs
        tab_frame = tk.Frame(right_panel, bg='#1a1a1a')
        tab_frame.pack(fill=tk.X)
        
        self.current_tab = tk.StringVar(value='flow')
        
        tabs = [
            ('flow', '🔀 Flow Visualization'),
            ('results', '📊 Results'),
            ('logs', '📝 Execution Logs'),
        ]
        
        for value, label in tabs:
            btn = tk.Button(tab_frame, text=label, 
                           command=lambda v=value: self.switch_tab(v),
                           bg='#2a2a2a' if value == 'flow' else '#1a1a1a',
                           fg='#ffffff', font=('Segoe UI', 10, 'bold'),
                           relief=tk.FLAT, padx=20, pady=12, cursor='hand2')
            btn.pack(side=tk.LEFT)
        
        # Content area
        self.content_area = tk.Frame(right_panel, bg='#0a0a0a')
        self.content_area.pack(fill=tk.BOTH, expand=True)
        
        self.show_flow_view()
        
    def switch_tab(self, tab):
        self.current_tab.set(tab)
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        if tab == 'flow':
            self.show_flow_view()
        elif tab == 'results':
            self.show_results_view()
        elif tab == 'logs':
            self.show_logs_view()
    
    def show_flow_view(self):
        canvas = tk.Canvas(self.content_area, bg='#0a0a0a', highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Draw grid
        for i in range(0, 2000, 50):
            canvas.create_line(i, 0, i, 2000, fill='#1a1a1a', width=1)
            canvas.create_line(0, i, 2000, i, fill='#1a1a1a', width=1)
        
        # Draw workflow visualization
        y_pos = 100
        x_start = 100
        
        selected_agents = [name for name, var in self.agent_vars.items() if var.get()]
        
        if not selected_agents:
            canvas.create_text(600, 300, text='Select agents to visualize workflow',
                             font=('Segoe UI', 16), fill='#888888')
            return
        
        mode = self.workflow_mode.get()
        
        if mode == 'sequential':
            for i, agent_name in enumerate(selected_agents):
                x = x_start
                y = y_pos + i * 120
                
                # Draw node
                canvas.create_rectangle(x, y, x+200, y+80, fill='#2a2a2a', outline='#00ff88', width=2)
                canvas.create_text(x+100, y+25, text=agent_name, font=('Segoe UI', 12, 'bold'), fill='#ffffff')
                canvas.create_text(x+100, y+50, text=self.agents[agent_name].specialty,
                                 font=('Segoe UI', 9), fill='#888888')
                
                # Draw arrow
                if i < len(selected_agents) - 1:
                    canvas.create_line(x+100, y+80, x+100, y+120, arrow=tk.LAST,
                                     fill='#00ff88', width=3)
        
        elif mode == 'parallel':
            for i, agent_name in enumerate(selected_agents):
                x = x_start + i * 220
                y = y_pos
                
                canvas.create_rectangle(x, y, x+200, y+80, fill='#2a2a2a', outline='#00ff88', width=2)
                canvas.create_text(x+100, y+25, text=agent_name, font=('Segoe UI', 12, 'bold'), fill='#ffffff')
                canvas.create_text(x+100, y+50, text=self.agents[agent_name].specialty,
                                 font=('Segoe UI', 9), fill='#888888')
        
        elif mode == 'hierarchical':
            # Manager at top
            canvas.create_rectangle(x_start+400, y_pos, x_start+600, y_pos+80,
                                  fill='#ff9500', outline='#ffffff', width=2)
            canvas.create_text(x_start+500, y_pos+40, text='🏢 Manager',
                             font=('Segoe UI', 14, 'bold'), fill='#ffffff')
            
            # Workers below
            for i, agent_name in enumerate(selected_agents):
                x = x_start + i * 220
                y = y_pos + 150
                
                canvas.create_rectangle(x, y, x+200, y+80, fill='#2a2a2a', outline='#00ff88', width=2)
                canvas.create_text(x+100, y+40, text=agent_name, font=('Segoe UI', 11, 'bold'), fill='#ffffff')
                
                # Connect to manager
                canvas.create_line(x+100, y, x_start+500, y_pos+80, fill='#00ff88', width=2)
    
    def show_results_view(self):
        scroll_frame = tk.Frame(self.content_area, bg='#0a0a0a')
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        if not self.workflow_results:
            tk.Label(scroll_frame, text='No results yet. Execute a workflow first.',
                    font=('Segoe UI', 14), bg='#0a0a0a', fg='#888888').pack(pady=100)
            return
        
        for i, result in enumerate(self.workflow_results):
            result_frame = tk.Frame(scroll_frame, bg='#1a1a1a')
            result_frame.pack(fill=tk.X, pady=10)
            
            # Header
            header = tk.Frame(result_frame, bg='#2a2a2a')
            header.pack(fill=tk.X)
            
            tk.Label(header, text=f"🤖 {result['agent']}", font=('Segoe UI', 12, 'bold'),
                    bg='#2a2a2a', fg='#00ff88').pack(side=tk.LEFT, padx=15, pady=10)
            
            tk.Label(header, text=f"Model: {result['model']}", font=('Segoe UI', 9),
                    bg='#2a2a2a', fg='#888888').pack(side=tk.LEFT)
            
            tk.Label(header, text=f"⏱️ {result['duration']:.2f}s", font=('Segoe UI', 9),
                    bg='#2a2a2a', fg='#888888').pack(side=tk.RIGHT, padx=15)
            
            # Content
            content = tk.Text(result_frame, bg='#0a0a0a', fg='#ffffff',
                            font=('Segoe UI', 10), wrap=tk.WORD, height=8, relief=tk.FLAT)
            content.pack(fill=tk.X, padx=15, pady=15)
            content.insert('1.0', result['result'])
            content.config(state='disabled')
    
    def show_logs_view(self):
        log_text = scrolledtext.ScrolledText(self.content_area, bg='#0a0a0a', fg='#00ff88',
                                            font=('Consolas', 10), wrap=tk.WORD, relief=tk.FLAT)
        log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        if not self.workflow_results:
            log_text.insert('1.0', '[INFO] No execution logs yet.\n')
            return
        
        for result in self.workflow_results:
            log_text.insert(tk.END, f"\n{'='*80}\n")
            log_text.insert(tk.END, f"[{result['timestamp']}] Agent: {result['agent']}\n")
            log_text.insert(tk.END, f"Model: {result['model']}\n")
            log_text.insert(tk.END, f"Duration: {result['duration']:.2f}s\n")
            log_text.insert(tk.END, f"Status: {'✓ SUCCESS' if result['success'] else '✗ FAILED'}\n")
            log_text.insert(tk.END, f"{'='*80}\n")
    
    def execute_workflow(self):
        task = self.task_input.get('1.0', tk.END).strip()
        if not task:
            messagebox.showwarning('Warning', 'Please enter a task description')
            return
        
        selected_agents = [name for name, var in self.agent_vars.items() if var.get()]
        if not selected_agents:
            messagebox.showwarning('Warning', 'Please select at least one agent')
            return
        
        self.workflow_results = []
        
        def run_workflow():
            mode = self.workflow_mode.get()
            
            if mode == 'sequential':
                self.run_sequential(task, selected_agents)
            elif mode == 'parallel':
                self.run_parallel(task, selected_agents)
            elif mode == 'debate':
                self.run_debate(task, selected_agents)
            elif mode == 'hierarchical':
                self.run_hierarchical(task, selected_agents)
            elif mode == 'autonomous':
                self.run_autonomous(task, selected_agents)
            
            self.root.after(0, lambda: self.switch_tab('results'))
        
        threading.Thread(target=run_workflow, daemon=True).start()
        messagebox.showinfo('Executing', f'Workflow started with {len(selected_agents)} agents in {self.workflow_mode.get()} mode')
    
    def run_sequential(self, task, agents):
        context = ""
        for agent_name in agents:
            start_time = time.time()
            agent = self.agents[agent_name]
            
            agent_task = f"{task}\n\nPrevious context: {context}" if context else task
            result = agent.execute(agent_task, context)
            
            duration = time.time() - start_time
            
            if result['success']:
                context += f"\n\n{agent_name}'s output:\n{result['result']}"
                self.workflow_results.append({
                    'agent': agent_name,
                    'model': result['model'],
                    'result': result['result'],
                    'success': True,
                    'duration': duration,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
    
    def run_parallel(self, task, agents):
        results = []
        threads = []
        
        def execute_agent(agent_name):
            start_time = time.time()
            agent = self.agents[agent_name]
            result = agent.execute(task)
            duration = time.time() - start_time
            
            if result['success']:
                results.append({
                    'agent': agent_name,
                    'model': result['model'],
                    'result': result['result'],
                    'success': True,
                    'duration': duration,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
        
        for agent_name in agents:
            t = threading.Thread(target=execute_agent, args=(agent_name,))
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
        
        self.workflow_results = results
    
    def run_debate(self, task, agents):
        rounds = 2
        context = task
        
        for round_num in range(rounds):
            for agent_name in agents:
                start_time = time.time()
                agent = self.agents[agent_name]
                
                debate_task = f"Round {round_num+1}: {task}\n\nPrevious discussion:\n{context}\n\nProvide your perspective and critique others:"
                result = agent.execute(debate_task)
                
                duration = time.time() - start_time
                
                if result['success']:
                    context += f"\n\n{agent_name} (Round {round_num+1}):\n{result['result']}"
                    self.workflow_results.append({
                        'agent': f"{agent_name} (Round {round_num+1})",
                        'model': result['model'],
                        'result': result['result'],
                        'success': True,
                        'duration': duration,
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
    
    def run_hierarchical(self, task, agents):
        # Manager breaks down task
        manager = self.agents['Strategist']
        manager_task = f"Break down this task into subtasks for these agents: {', '.join(agents)}\n\nTask: {task}"
        
        start_time = time.time()
        manager_result = manager.execute(manager_task)
        duration = time.time() - start_time
        
        if manager_result['success']:
            self.workflow_results.append({
                'agent': 'Manager (Strategist)',
                'model': manager_result['model'],
                'result': manager_result['result'],
                'success': True,
                'duration': duration,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            
            # Workers execute
            self.run_parallel(task, agents)
    
    def run_autonomous(self, task, agents):
        # Agents self-organize
        self.run_debate(task, agents)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = NexusAgenticAI()
    app.run()
