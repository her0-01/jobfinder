"""
NEXUS OS - Groq AI Integration
Multi-agent AI system with Groq
"""

import requests
import json
import configparser
import os

class GroqAIAgent:
    def __init__(self, config_path='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        self.api_key = self.config.get('GROQ', 'API_KEY', fallback='')
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        
        self.agents = {
            'main': self.config.get('AI_AGENTS', 'AGENT_1', fallback='llama-3.3-70b-versatile'),
            'creative': self.config.get('AI_AGENTS', 'AGENT_2', fallback='llama-3.1-8b-instant'),
            'fast': self.config.get('AI_AGENTS', 'AGENT_3', fallback='gemma2-9b-it')
        }
        
    def query(self, prompt, agent='main', temperature=0.7):
        """Query Groq AI"""
        if not self.api_key or self.api_key == 'your_groq_api_key_here':
            return {"response": "⚠️ Please add your Groq API key in config.ini", "error": True}
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.agents.get(agent, self.agents['main']),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": 1024
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return {
                    "response": result['choices'][0]['message']['content'],
                    "model": data['model'],
                    "error": False
                }
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f": {error_data.get('error', {}).get('message', response.text)}"
                except:
                    error_msg += f": {response.text[:200]}"
                return {"response": error_msg, "error": True}
        except requests.exceptions.Timeout:
            return {"response": "Request timeout - Groq API took too long", "error": True}
        except requests.exceptions.ConnectionError:
            return {"response": "Connection error - Check internet connection", "error": True}
        except Exception as e:
            return {"response": f"Error: {type(e).__name__}: {str(e)}", "error": True}
    
    def multi_agent_query(self, prompt):
        """Query multiple agents and combine responses"""
        results = {}
        for agent_name in ['main', 'creative', 'fast']:
            result = self.query(prompt, agent=agent_name, temperature=0.8)
            results[agent_name] = result
        return results
    
    def chat(self, messages, agent='main'):
        """Chat with context"""
        if not self.api_key or self.api_key == 'your_groq_api_key_here':
            return {"response": "⚠️ Please add your Groq API key in config.ini", "error": True}
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.agents.get(agent, self.agents['main']),
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2048
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return {
                    "response": result['choices'][0]['message']['content'],
                    "model": data['model'],
                    "error": False
                }
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f": {error_data.get('error', {}).get('message', response.text)}"
                except:
                    error_msg += f": {response.text[:200]}"
                return {"response": error_msg, "error": True}
        except requests.exceptions.Timeout:
            return {"response": "Request timeout - Groq API took too long", "error": True}
        except requests.exceptions.ConnectionError:
            return {"response": "Connection error - Check internet connection", "error": True}
        except Exception as e:
            return {"response": f"Error: {type(e).__name__}: {str(e)}", "error": True}

# Global AI instance
groq_ai = GroqAIAgent()
