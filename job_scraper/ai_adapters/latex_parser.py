import re

class LaTeXParser:
    """Parser pour extraire le contenu d'un CV LaTeX"""
    
    @staticmethod
    def extract_text(latex_content):
        """Extraire le texte d'un fichier LaTeX"""
        # Supprimer les commentaires
        text = re.sub(r'%.*', '', latex_content)
        
        # Supprimer le préambule
        text = re.sub(r'\\documentclass.*?\\begin{document}', '', text, flags=re.DOTALL)
        text = re.sub(r'\\end{document}', '', text)
        
        # Extraire les sections importantes
        sections = {}
        
        # Nom et contact
        name = re.search(r'\\name{([^}]+)}', text)
        if name:
            sections['name'] = name.group(1)
        
        email = re.search(r'\\email{([^}]+)}', text)
        if email:
            sections['email'] = email.group(1)
        
        phone = re.search(r'\\phone{([^}]+)}', text)
        if phone:
            sections['phone'] = phone.group(1)
        
        # Nettoyer les commandes LaTeX
        text = re.sub(r'\\[a-zA-Z]+\*?{([^}]*)}', r'\1', text)
        text = re.sub(r'\\[a-zA-Z]+\*?', '', text)
        text = re.sub(r'[{}]', '', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    @staticmethod
    def generate_adapted_latex(base_latex, adapted_content):
        """Générer un nouveau LaTeX avec contenu adapté"""
        # Garder le préambule original
        preamble = re.search(r'(.*?\\begin{document})', base_latex, flags=re.DOTALL)
        end = r'\end{document}'
        
        if preamble:
            return f"{preamble.group(1)}\n\n{adapted_content}\n\n{end}"
        else:
            return adapted_content
