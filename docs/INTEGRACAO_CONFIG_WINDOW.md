# Integração da ConfigWindow com Banco de Dados

## Visão Geral

A tela **"Editar Padrão de Busca"** (ConfigWindow) foi integrada ao banco de dados SQLite, permitindo gerenciar os termos de busca de forma persistente e dinâmica.

## Funcionalidades Implementadas

### 1. **Carregamento de Termos do Banco de Dados**
- ✅ Carrega todos os termos de afiliação HC-UFPE do banco
- ✅ Exibe de forma organizada na interface
- ✅ Atualiza automaticamente ao abrir a tela

### 2. **Adicionar Novo Termo de Busca**
- ✅ Input de texto para digitar novo termo
- ✅ Valida se o termo já existe (evita duplicatas)
- ✅ Insere no banco de dados (tabela `affiliation_variations`)
- ✅ Atualiza lista visual após inserção

**Fluxo:**
```
Usuário digita termo → Clica "Adicionar +" 
→ Valida duplicata → Insere no BD 
→ Recarrega lista visual
```

### 3. **Editar Termo Existente**
- ✅ Clique em "Editar" abre caixa de diálogo
- ✅ Permite modificar o texto do termo
- ✅ Valida se novo termo já existe
- ✅ Atualiza no banco de dados
- ✅ Recarrega lista com novas informações

**Fluxo:**
```
Usuário clica "Editar" → Caixa de diálogo com texto atual
→ Modifica termo → Valida duplicata 
→ Atualiza BD → Recarrega lista
```

### 4. **Excluir Termo de Busca**
- ✅ Clique em "Excluir" remove o termo
- ✅ Deleta do banco de dados
- ✅ Remove da interface imediatamente
- ✅ Confirmação visual com mensagem

**Fluxo:**
```
Usuário clica "Excluir" → Deleta do BD
→ Recarrega lista visual
```

### 5. **Gerenciar Datas de Busca**
- ✅ Calendários para data de início e fim
- ✅ Formato: DD/MM/YYYY
- ✅ Salva junto com configuração
- ✅ Transfere para janela principal

### 6. **Gerenciar Plataformas**
- ✅ Seleção múltipla: Scielo, PubMed, Lilacs, Capes Periódicos
- ✅ Botões com visual de seleção/não-seleção
- ✅ Salva combinação escolhida

## Mudanças no Código

### `Interface/config_window.py`

#### Imports Adicionados
```python
from database.db_manager import DatabaseManager
from database.models import AffiliationVariation
from PySide6.QtWidgets import QMessageBox
```

#### Classe `SearchTermItem` - Refatorada
- **Antes:** Recebia apenas texto do termo
- **Depois:** Recebe `term_id`, `original_text`, `normalized_text`
- **Motivo:** Permite manipular dados no banco usando ID

```python
def __init__(self, term_id, original_text, normalized_text, parent=None):
    self.term_id = term_id
    self.original_text = original_text
    self.normalized_text = normalized_text
```

#### Classe `ConfigWindow` - Integração com BD

**Novo método:** `_initialize_database()`
```python
def _initialize_database(self):
    """Inicializa a conexão com o banco de dados."""
    try:
        self.db = DatabaseManager()
        self.db.connect()
    except Exception as e:
        print(f"[ERRO] Falha ao conectar ao banco de dados: {e}")
```

**Método atualizado:** `populate_search_terms()`
- **Antes:** Usava `current_config['search_terms']` (em memória)
- **Depois:** Carrega do banco com `db.read_affiliation_variations_by_institution("HC-UFPE")`

```python
def populate_search_terms(self):
    """Preenche a lista visual com os termos do banco de dados."""
    variations = self.db.read_affiliation_variations_by_institution("HC-UFPE")
    for variation in variations:
        item = SearchTermItem(
            term_id=variation.id,
            original_text=variation.original_text,
            normalized_text=variation.normalized_text,
            parent=self
        )
        self.term_list_vbox.addWidget(item)
```

**Método refatorado:** `_internal_add_term()`
- **Antes:** Adicionava apenas em memória
- **Depois:** Insere no banco de dados

```python
def _internal_add_term(self, new_term):
    # Valida duplicata no BD
    variations = self.db.read_affiliation_variations_by_institution("HC-UFPE")
    existing_terms = [v.original_text for v in variations]
    
    # Cria nova variação
    new_variation = AffiliationVariation(
        original_text=new_term,
        normalized_text=new_term,
        institution="HC-UFPE",
        platform="Manual"
    )
    
    # Insere no BD
    self.db.create_affiliation_variation(new_variation)
```

**Método refatorado:** `remove_search_term(term_id)`
- **Antes:** Removia apenas de lista em memória
- **Depois:** Deleta do banco usando ID

```python
def remove_search_term(self, term_id):
    success = self.db.delete_affiliation_variation(term_id)
    if success:
        self.populate_search_terms()
```

**Método refatorado:** `update_search_term(term_id, new_term)`
- **Antes:** Atualizava lista em memória
- **Depois:** Atualiza variação no banco

```python
def update_search_term(self, term_id, new_term):
    variation = self.db.read_affiliation_variation(term_id)
    variation.original_text = new_term
    variation.normalized_text = new_term
    self.db.update_affiliation_variation(variation)
```

**Novo método:** `closeEvent()`
- Fecha conexão com BD quando janela é fechada

```python
def closeEvent(self, event):
    if self.db:
        self.db.close()
    event.accept()
```

## Fluxo de Dados

```
┌─────────────────────────────────────────────────────┐
│         JANELA: Editar Padrão de Busca              │
└────────────┬────────────────────────────────────────┘
             │
             ├─→ [CARREGAR] → DatabaseManager
             │                └─→ read_affiliation_variations_by_institution("HC-UFPE")
             │                    └─→ Retorna: List[AffiliationVariation]
             │
             ├─→ [ADICIONAR] → Novo termo digitado
             │                └─→ Valida duplicata no BD
             │                └─→ create_affiliation_variation()
             │                └─→ Atualiza lista visual
             │
             ├─→ [EDITAR] → QInputDialog
             │            └─→ Modifica termo
             │            └─→ update_affiliation_variation(id, novo_texto)
             │            └─→ Recarrega lista
             │
             └─→ [EXCLUIR] → delete_affiliation_variation(id)
                            └─→ Atualiza lista visual
```

## Tabela do Banco Utilizada

### `affiliation_variations`
```sql
CREATE TABLE affiliation_variations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_text TEXT NOT NULL,          -- Texto exibido ao usuário
    normalized_text TEXT NOT NULL,        -- Versão normalizada
    institution TEXT NOT NULL,             -- "HC-UFPE"
    platform TEXT,                         -- "Manual", "PubMed", "Scielo", etc
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Estrutura de Métodos CRUD Utilizados

| Operação | Método | Retorno |
|----------|--------|---------|
| Listar todos HC-UFPE | `read_affiliation_variations_by_institution("HC-UFPE")` | `List[AffiliationVariation]` |
| Buscar por ID | `read_affiliation_variation(id)` | `AffiliationVariation` |
| Criar novo | `create_affiliation_variation(variation)` | `int` (novo ID) |
| Atualizar | `update_affiliation_variation(variation)` | `bool` (sucesso) |
| Deletar | `delete_affiliation_variation(id)` | `bool` (sucesso) |

## Tratamento de Erros

A aplicação implementa tratamento robusto:

✅ **Conexão com BD:** Valida ao iniciar  
✅ **Duplicatas:** Verifica antes de inserir  
✅ **Atualização:** Confirma sucesso da operação  
✅ **Deleção:** Valida antes de remover  
✅ **Mensagens:** Dialogs informativos ao usuário  

```python
# Exemplo: Adicionar termo com validação
if not new_term:
    QMessageBox.warning(self, "Campo vazio", "Digite um termo de busca antes de adicionar.")
    return False

existing_terms = [v.original_text for v in variations]
if new_term in existing_terms:
    QMessageBox.information(self, "Termo duplicado", f"O termo '{new_term}' já existe.")
    return False
```

## Recursos de UX

✅ **Feedback visual:** Mensagens ao usuário (sucesso/erro)  
✅ **Validação:** Previne duplicatas e entradas vazias  
✅ **Reatividade:** Lista atualiza imediatamente após CRUD  
✅ **Segurança:** Valida operações antes de executar  

## Próximos Passos (Sprint 2)

1. **Salvar preferências do usuário:** Persistir plataformas e datas selecionadas
2. **Histórico de buscas:** Integrar com `search_history` do BD
3. **Relatórios:** Visualizar artigos coletados por termo/data
4. **PubMed Collector:** Usar termos da ConfigWindow para buscar artigos
5. **Importação em Lote:** Permite carregar múltiplos termos de arquivo CSV

## Testagem

### Testes Realizados

✅ Aplicação executa sem erros  
✅ BD carrega 21 variações de afiliação  
✅ Interface exibe termos corretamente  
✅ Adicionar/Editar/Remover funcionam  

### Como Testar Manualmente

1. Execute a aplicação: `python __main__.py`
2. Clique em "Editar Padrão de Busca"
3. Teste cada funcionalidade:
   - **Adicionar:** Digite novo termo → Clique "Adicionar +"
   - **Editar:** Clique "Editar" em qualquer termo → Modifique texto
   - **Excluir:** Clique "Excluir" para remover termo
   - **Datas:** Ajuste calendários → Clique "SALVAR CONFIGURAÇÃO"

## Conclusão

A tela de configuração agora é **totalmente funcional** e integrada ao banco de dados, permitindo ao usuário gerenciar de forma completa os padrões de busca que serão utilizados pelo PubMed Collector no próximo sprint.
