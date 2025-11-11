# 📖 GUIA DE USO: Tela de Configuração de Padrão de Busca

## 🎯 Objetivo

Gerenciar os termos de busca HC-UFPE que serão utilizados para coletar artigos das plataformas científicas (PubMed, Scielo, Lilacs, Capes Periódicos).

---

## 🚀 Como Usar

### Abrir a Tela de Configuração

1. Execute a aplicação:
   ```powershell
   . .\venv\Scripts\Activate.ps1
   python __main__.py
   ```

2. Clique no botão **"Editar Padrão de Busca"** na janela principal

3. A tela de configuração abrirá com 22 termos já carregados do banco de dados

---

## 📋 Funcionalidades

### 1. Visualizar Termos Existentes

Ao abrir a tela, você verá uma lista de todos os termos HC-UFPE carregados automaticamente:

```
┌─────────────────────────────────────────────────────────────┐
│ Termos de Busca                                             │
├─────────────────────────────────────────────────────────────┤
│ "Hospital das Clinicas - UFPE"        [Editar] [Excluir]  │
│ "Hospital das Clínicas da UFPE"       [Editar] [Excluir]  │
│ "HC UFPE"                             [Editar] [Excluir]  │
│ "HC EBSERH"                           [Editar] [Excluir]  │
│ ... (e mais 18 termos)                                     │
└─────────────────────────────────────────────────────────────┘
```

**Total:** 22 variações de afiliação HC-UFPE

---

### 2. Adicionar Novo Termo

#### Passo 1: Digite o novo termo
```
┌──────────────────────────────┬─────────┐
│ Adicionar Termo de busca     │         │
├──────────────────────────────┴─────────┤
│ [Campo de entrada]           [+ Adicionar]
│ Ex: "Hospital das Clínicas Pernambuco"   │
└──────────────────────────────────────────┘
```

#### Passo 2: Clique em "Adicionar +"

#### Passo 3: Confirmação
- ✅ Se sucesso: Termo aparece na lista
- ⚠️ Se já existe: Mensagem "O termo já existe"
- ⚠️ Se vazio: Mensagem "Digite um termo antes de adicionar"

---

### 3. Editar Termo Existente

#### Passo 1: Localize o termo na lista

#### Passo 2: Clique no botão **"Editar"**

#### Passo 3: Modifique o texto
```
┌──────────────────────────────────────┐
│ Editar Termo de Busca                │
├──────────────────────────────────────┤
│ Novo Termo:                          │
│ [Campo com texto atual selecionado]  │
│                                      │
│           [OK]  [Cancelar]           │
└──────────────────────────────────────┘
```

#### Passo 4: Clique "OK"
- ✅ Se sucesso: Termo atualizado na lista
- ⚠️ Se duplica outro: Mensagem de erro

---

### 4. Excluir Termo

#### Passo 1: Localize o termo na lista

#### Passo 2: Clique no botão **"Excluir"**

#### Resultado
- ✅ Termo é removido imediatamente
- ✅ Desaparece da lista
- ✅ Deletado do banco de dados

---

### 5. Configurar Período de Busca

Define em qual período os artigos serão procurados.

#### Passo 1: Clique no campo "A partir de"
```
┌──────────────────┐
│ Período de busca │
├──────────────────┤
│ A partir de [📅] → Abre calendário
│ Até        [📅] → Abre calendário
└──────────────────┘
```

#### Passo 2: Selecione a data inicial
- Clique na data desejada
- Formato: DD/MM/YYYY

#### Passo 3: Clique em "Até" e selecione data final

#### Resultado
- ✅ Datas salvas
- ✅ Usado em próximas buscas

---

### 6. Selecionar Plataformas

Escolha quais plataformas científicas buscar.

#### Disponíveis:
- **Scielo** - Biblioteca científica brasileira
- **PubMed** - Base de dados biomédica
- **Lilacs** - Literatura Latino-Americana
- **Capes Periódicos** - Periódicos da Capes

#### Como usar:
1. Clique no botão da plataforma para ativar/desativar
2. Botão ativo: Fundo azul, texto branco
3. Botão inativo: Fundo branco, texto azul

---

### 7. Salvar Configuração

#### Clique em "SALVAR CONFIGURAÇÃO"

```
┌────────────────────────────────────┐
│    SALVAR CONFIGURAÇÃO             │
│                                    │
│ ✅ Termos salvos                   │
│ ✅ Datas salvas                    │
│ ✅ Plataformas salvas              │
│                                    │
│ [OK - Voltar à tela principal]    │
└────────────────────────────────────┘
```

---

## 📊 Exemplos de Uso

### Cenário 1: Adicionar novo termo de busca

**Objetivo:** Incluir um novo padrão de busca para HC-UFPE

**Passos:**
1. Abra ConfigWindow
2. No campo "Adicionar Termo de busca", digite:
   ```
   Hospital das Clínicas - Universidade Federal de Pernambuco
   ```
3. Clique em "Adicionar +"
4. Termo aparece na lista
5. Clique "SALVAR CONFIGURAÇÃO"

**Resultado:** Novo termo será usado nas próximas buscas

---

### Cenário 2: Corrigir um termo com erro

**Objetivo:** Modificar um termo que foi digitado errado

**Passos:**
1. Abra ConfigWindow
2. Procure o termo com erro
3. Clique em "Editar"
4. Corrija o texto
5. Clique "OK"
6. Clique "SALVAR CONFIGURAÇÃO"

**Resultado:** Termo corrigido no banco de dados

---

### Cenário 3: Remover termos desnecessários

**Objetivo:** Deletar termos que não serão mais usados

**Passos:**
1. Abra ConfigWindow
2. Localize o termo a remover
3. Clique em "Excluir"
4. Termo desaparece
5. Clique "SALVAR CONFIGURAÇÃO"

**Resultado:** Termo removido permanentemente

---

### Cenário 4: Configurar período de busca

**Objetivo:** Buscar apenas artigos publicados em 2024

**Passos:**
1. Abra ConfigWindow
2. No campo "Período de busca", clique em "A partir de"
3. Selecione: 01/01/2024
4. Clique em "Até"
5. Selecione: 31/12/2024
6. Clique "SALVAR CONFIGURAÇÃO"

**Resultado:** Próximas buscas usarão esse período

---

## ⚠️ Validações e Mensagens

### Mensagens de Sucesso
```
✅ "Configuração salva com sucesso!"
   → Significa que as alterações foram gravadas no banco
```

### Mensagens de Aviso
```
⚠️ "O termo 'XXX' já existe."
   → Você tentou adicionar um termo duplicado
   → Solução: Use um termo diferente
```

```
⚠️ "Digite um termo de busca antes de adicionar."
   → O campo de entrada está vazio
   → Solução: Preencha o campo com um termo válido
```

### Mensagens de Erro
```
❌ "Banco de dados não conectado."
   → Erro de conexão com o BD
   → Solução: Reinicie a aplicação
```

```
❌ "Falha ao remover termo."
   → Erro ao deletar no banco
   → Solução: Tente novamente ou reinicie
```

---

## 💾 Onde os Dados São Salvos?

### Banco de Dados: `nexus_pesquisa.db`
- **Localização:** Raiz do projeto
- **Tabela:** `affiliation_variations`
- **Colunas:**
  - `id` - Identificador único
  - `original_text` - Texto exibido (o que você escreve)
  - `normalized_text` - Versão normalizada
  - `institution` - "HC-UFPE"
  - `platform` - Origem (Manual, PubMed, etc)
  - `created_at` - Data de criação
  - `updated_at` - Última modificação

### Acesso Direto (SQL)
```sql
SELECT * FROM affiliation_variations 
WHERE institution = "HC-UFPE" 
ORDER BY original_text;

-- Retorna: Todos os 22 (ou mais) termos
```

---

## 🔍 Verificar Dados

### Via Aplicação
1. Abra ConfigWindow
2. Veja a lista de termos carregados

### Via Terminal (SQL)
```powershell
# Contar total de termos
python -c "
from database.db_manager import DatabaseManager
db = DatabaseManager()
vars = db.read_affiliation_variations_by_institution('HC-UFPE')
print(f'Total: {len(vars)} termos')
"

# Resultado: Total: 22 termos ✅
```

---

## 🆘 Troubleshooting

### P: Não consigo adicionar um termo
**R:** Verifique se:
- Digitou corretamente no campo de entrada
- O termo não é um duplicata
- A aplicação tem conexão com BD
- Clicou no botão "Adicionar +"

### P: Um termo foi deletado acidentalmente
**R:** O termo está no banco de dados histórico. Para recuperar:
1. Abra ConfigWindow
2. Adicione novamente o termo
3. Clique "SALVAR CONFIGURAÇÃO"

### P: A lista está vazia
**R:** Significa que não há termos HC-UFPE no banco. Para inicializar:
1. Reinicie a aplicação
2. Execute: `python test_config_integration.py`
3. Verifique a saída de carregamento

### P: Erro "Banco de dados não conectado"
**R:** 
1. Fechione a aplicação
2. Verifique se `nexus_pesquisa.db` existe na raiz
3. Abra novamente
4. Se persistir, delete o BD e reinicie (recriará automaticamente)

---

## 📱 Interface

```
┌─────────────────────────────────────────────────┐
│ ← │ Editar Padrão de Busca           © EBSERH │
├─────────────────────────────────────────────────┤
│                                                 │
│ Selecione os Filtros                           │
│ Banco de dados                                 │
│ [Scielo] [PubMed] [Lilacs] [Capes Periódicos]│
│                                                 │
│ Período de busca                               │
│ A partir de: [01/01/2021] Até: [10/11/2025]   │
│                                                 │
│ Adicionar Termos de Busca                      │
│ [Adicionar Termo de busca] [+ Adicionar]       │
│                                                 │
│ Termos de Busca                                │
│ ┌─────────────────────────────────────────┐   │
│ │ "Hospital das Clinicas - UFPE"          │   │
│ │ [Editar] [Excluir]                     │   │
│ ├─────────────────────────────────────────┤   │
│ │ "Hospital das Clínicas da UFPE"        │   │
│ │ [Editar] [Excluir]                     │   │
│ ├─────────────────────────────────────────┤   │
│ │ "HC UFPE"                              │   │
│ │ [Editar] [Excluir]                     │   │
│ ├─────────────────────────────────────────┤   │
│ │ ... (19 termos adicionais) ...          │   │
│ └─────────────────────────────────────────┘   │
│                                                 │
│ [SALVAR CONFIGURAÇÃO]                         │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 📞 Suporte

Se tiver dúvidas ou problemas:

1. Verifique este guia
2. Consulte `INTEGRACAO_CONFIG_WINDOW.md` (técnico)
3. Abra uma issue no repositório
4. Contate: tiago.renan@ufpe.br

---

**Data:** 10 de Novembro de 2025  
**Versão:** 1.0  
**Status:** ✅ Pronto para Uso
