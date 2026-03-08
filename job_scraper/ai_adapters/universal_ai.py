"""
Adaptateur universel pour tous les providers IA
Supporte: Groq, OpenAI, Gemini
"""
import json
from typing import List, Dict, Optional

class UniversalAIAdapter:
    """Adaptateur universel pour tous les providers IA"""
    
    def __init__(self, provider: str, api_key: str):
        self.provider = provider.lower()
        self.api_key = api_key
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialise le client selon le provider"""
        if self.provider == 'groq':
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
        
        elif self.provider == 'openai':
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        
        elif self.provider == 'gemini':
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai
    
    def get_available_models(self) -> List[str]:
        """Retourne la liste des modèles disponibles"""
        if self.provider == 'groq':
            return [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "meta-llama/llama-4-maverick-17b-128e-instruct",
                "qwen/qwen3-32b"
            ]
        
        elif self.provider == 'openai':
            return [
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-4-turbo",
                "gpt-3.5-turbo"
            ]
        
        elif self.provider == 'gemini':
            return [
                "models/gemini-2.5-flash",
                "models/gemini-2.0-flash",
                "models/gemini-flash-latest",
                "models/gemini-pro-latest"
            ]
        
        return []
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 500,
        json_mode: bool = False
    ) -> str:
        """
        Appel universel de chat completion
        Fonctionne avec tous les providers
        """
        if not model:
            model = self.get_available_models()[0]
        
        try:
            if self.provider == 'groq':
                kwargs = {
                    "messages": messages,
                    "model": model,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                if json_mode:
                    kwargs["response_format"] = {"type": "json_object"}
                
                response = self.client.chat.completions.create(**kwargs)
                return response.choices[0].message.content
            
            elif self.provider == 'openai':
                kwargs = {
                    "messages": messages,
                    "model": model,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                if json_mode:
                    kwargs["response_format"] = {"type": "json_object"}
                
                response = self.client.chat.completions.create(**kwargs)
                return response.choices[0].message.content
            
            elif self.provider == 'gemini':
                model_obj = self.client.GenerativeModel(model)
                
                # Construire le prompt (Gemini n'a pas de rôles séparés)
                prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
                
                # IMPORTANT: Augmenter max_tokens pour éviter troncature
                # Gemini compte différemment, multiplier par 1.5
                adjusted_max_tokens = int(max_tokens * 1.5)
                
                generation_config = {
                    "temperature": temperature,
                    "max_output_tokens": adjusted_max_tokens,
                    "top_p": 0.95,
                    "top_k": 40,
                    "candidate_count": 1
                }
                
                # Pour JSON mode, prompt strict et court
                if json_mode:
                    # Simplifier le prompt pour réduire l'input
                    prompt = messages[-1]['content']  # Prendre seulement le dernier message
                    prompt += "\n\nRéponds UNIQUEMENT avec JSON valide. Rien d'autre."
                
                # Safety settings pour éviter les blocages
                safety_settings = [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                ]
                
                response = model_obj.generate_content(
                    prompt,
                    generation_config=generation_config,
                    safety_settings=safety_settings
                )
                
                # Vérifier la réponse
                if not response or not hasattr(response, 'text') or not response.text:
                    # Si pas de texte, vérifier les candidats
                    if hasattr(response, 'candidates') and response.candidates:
                        candidate = response.candidates[0]
                        if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                            text = ''.join([part.text for part in candidate.content.parts if hasattr(part, 'text')])
                            if text:
                                return text.strip()
                    raise Exception("Réponse vide de Gemini")
                
                text = response.text.strip()
                
                # Nettoyage JSON agressif
                if json_mode:
                    # Retirer markdown
                    if '```' in text:
                        # Extraire le contenu entre ```
                        parts = text.split('```')
                        for part in parts:
                            part = part.strip()
                            if part.startswith('json'):
                                part = part[4:].strip()
                            if part and (part.startswith('{') or part.startswith('[')):
                                text = part
                                break
                    
                    # Extraire le JSON même si incomplet
                    if '{' in text:
                        start = text.index('{')
                        text = text[start:]
                        
                        # Compter les accolades
                        open_braces = text.count('{')
                        close_braces = text.count('}')
                        
                        # Si troncature, compléter le JSON
                        if open_braces > close_braces:
                            # Fermer les accolades manquantes
                            text += '}' * (open_braces - close_braces)
                        
                        # Si string non terminée, la fermer
                        if text.count('"') % 2 != 0:
                            # Trouver la dernière quote et fermer
                            last_quote = text.rfind('"')
                            if last_quote > 0 and text[last_quote-1] != '\\':
                                # Ajouter une quote fermante avant la dernière accolade
                                if text.endswith('}'):
                                    text = text[:-1] + '"}'
                                else:
                                    text += '"'
                
                return text
        
        except Exception as e:
            raise Exception(f"Erreur {self.provider}: {str(e)}")
    
    def chat_completion_with_fallback(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 500,
        json_mode: bool = False
    ) -> str:
        """
        Essaie tous les modèles disponibles jusqu'à ce qu'un fonctionne
        Garantit une réponse peu importe le provider
        """
        models = self.get_available_models()
        last_error = None
        
        for i, model in enumerate(models):
            try:
                result = self.chat_completion(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    json_mode=json_mode
                )
                
                # Vérifier que la réponse n'est pas vide
                if result and result.strip():
                    return result
                    
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                
                # Si rate limit, essayer le modèle suivant
                if "rate_limit" in error_str or "429" in error_str or "quota" in error_str:
                    continue
                # Si erreur de modèle, essayer le suivant
                elif "model" in error_str or "not found" in error_str:
                    continue
                # Pour toute autre erreur, continuer quand même
                else:
                    continue
        
        # Si tous les modèles ont échoué, retourner un JSON par défaut si json_mode
        if json_mode:
            return '{"keywords":"q","location":"location","contract":"contract"}'
        
        raise Exception(f"Tous les modèles {self.provider} ont échoué: {last_error}")


def load_ai_config():
    """Charge la config IA depuis config.ini"""
    import configparser
    import os
    config = configparser.ConfigParser()
    
    config_paths = [
        'config.ini',
        os.path.join(os.path.dirname(__file__), '..', 'config.ini'),
        os.path.join(os.path.dirname(__file__), '..', '..', 'config.ini')
    ]
    
    for path in config_paths:
        if os.path.exists(path):
            config.read(path)
            break
    
    provider = config.get('API', 'ai_provider', fallback='groq')
    
    if provider == 'groq':
        api_key = config.get('API', 'groq_api_key', fallback='')
    elif provider == 'openai':
        api_key = config.get('API', 'openai_api_key', fallback='')
    elif provider == 'gemini':
        api_key = config.get('API', 'gemini_api_key', fallback='')
    else:
        api_key = ''
    
    return provider, api_key


def get_ai_adapter() -> UniversalAIAdapter:
    """Retourne l'adaptateur IA configuré"""
    provider, api_key = load_ai_config()
    return UniversalAIAdapter(provider, api_key)
