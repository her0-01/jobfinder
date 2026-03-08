from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import markdown
from pathlib import Path
import subprocess
import tempfile
import os
import shutil

class PDFGenerator:
    """Génère des PDFs professionnels pour CV et lettres"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """Configure les styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor='#2C3E50',
            spaceAfter=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))
    
    def generate_cv_pdf(self, cv_markdown, output_path):
        """Génère PDF du CV depuis Markdown"""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # Convertir Markdown en HTML puis en Paragraphes
        lines = cv_markdown.split('\n')
        
        for line in lines:
            if not line.strip():
                story.append(Spacer(1, 0.3*cm))
                continue
            
            # Titres
            if line.startswith('# '):
                text = line.replace('# ', '')
                story.append(Paragraph(text, self.styles['CustomTitle']))
            elif line.startswith('## '):
                text = line.replace('## ', '')
                story.append(Paragraph(text, self.styles['Heading2']))
            elif line.startswith('### '):
                text = line.replace('### ', '')
                story.append(Paragraph(text, self.styles['Heading3']))
            # Listes
            elif line.startswith('- ') or line.startswith('* '):
                text = '• ' + line[2:]
                story.append(Paragraph(text, self.styles['CustomBody']))
            # Texte normal
            else:
                # Remplacer markdown bold/italic
                text = line.replace('**', '<b>').replace('**', '</b>')
                text = text.replace('*', '<i>').replace('*', '</i>')
                story.append(Paragraph(text, self.styles['CustomBody']))
        
        doc.build(story)
        return output_path
    
    def generate_letter_pdf(self, letter_text, profile, output_path):
        """Génère PDF de la lettre de motivation"""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2.5*cm,
            leftMargin=2.5*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # En-tête
        header_style = ParagraphStyle(
            'Header',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT
        )
        
        story.append(Paragraph(f"<b>{profile['name']}</b>", header_style))
        story.append(Paragraph(profile['email'], header_style))
        story.append(Paragraph(profile['phone'], header_style))
        story.append(Spacer(1, 1*cm))
        
        # Corps de la lettre
        paragraphs = letter_text.split('\n\n')
        
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), self.styles['CustomBody']))
                story.append(Spacer(1, 0.5*cm))
        
        doc.build(story)
        return output_path

    def compile_latex_to_pdf(self, latex_content, output_path):
        """Compile LaTeX en PDF"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False, encoding='utf-8') as f:
                f.write(latex_content)
                tex_file = f.name
            
            temp_dir = os.path.dirname(tex_file)
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', '-output-directory', temp_dir, tex_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            pdf_temp = tex_file.replace('.tex', '.pdf')
            
            if os.path.exists(pdf_temp):
                shutil.move(pdf_temp, output_path)
                for ext in ['.tex', '.aux', '.log', '.out']:
                    temp_file = tex_file.replace('.tex', ext)
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                return output_path
            else:
                print("  ⚠️ Erreur compilation LaTeX, fallback vers Markdown")
                from ai_adapters.latex_parser import LaTeXParser
                text = LaTeXParser.extract_text(latex_content)
                return self.generate_cv_pdf(text, output_path)
                
        except FileNotFoundError:
            print("  ⚠️ pdflatex non installé, fallback vers Markdown")
            from ai_adapters.latex_parser import LaTeXParser
            text = LaTeXParser.extract_text(latex_content)
            return self.generate_cv_pdf(text, output_path)
        except Exception as e:
            print(f"  ⚠️ Erreur: {e}, fallback vers Markdown")
            from ai_adapters.latex_parser import LaTeXParser
            text = LaTeXParser.extract_text(latex_content)
            return self.generate_cv_pdf(text, output_path)
