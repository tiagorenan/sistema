#!/usr/bin/env python3
"""
Script para copiar todos os arquivos markdown para a pasta docs/
"""

import os
import shutil

def copy_markdown_files():
    """Copia todos os arquivos .md para a pasta docs/"""
    
    # Arquivos que já estão em docs
    excluded = {'README.md', 'DOCUMENTACAO.md', 'PROGRESSO.md'}
    
    # Listar arquivos markdown
    md_files = [f for f in os.listdir('.') if f.endswith('.md') and f not in excluded]
    
    copied = 0
    for md_file in md_files:
        dest = os.path.join('docs', md_file)
        
        # Não copiar se já existe
        if not os.path.exists(dest):
            shutil.copy(md_file, dest)
            print(f"[OK] Copiado: {md_file} → docs/{md_file}")
            copied += 1
        else:
            print(f"[SKIP] Já existe: docs/{md_file}")
    
    print(f"\n[SUMMARY] {copied} arquivos copiados para docs/")
    print(f"[TOTAL] {len(md_files)} arquivos markdown organizados")

if __name__ == '__main__':
    copy_markdown_files()
