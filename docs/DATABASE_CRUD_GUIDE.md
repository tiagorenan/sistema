## 📚 DOCUMENTAÇÃO DO CRUD - NEXUS PESQUISA

Implementação completa de CRUD (Create, Read, Update, Delete) para o banco de dados SQLite.

---

## 🗂️ Estrutura de Arquivos

```
database/
├── __init__.py              # Exporta classes principais
├── models.py                # Modelos de dados (Dataclasses)
├── db_manager.py            # Gerenciador de BD com CRUD
├── queries.py               # Queries SQL predefinidas
└── test_crud.py             # Testes de funcionalidade
```

---

## 📋 Modelos Disponíveis

### 1. **AffiliationVariation**
Representa variações de nomes de instituições/hospitais.

```python
from database.models import AffiliationVariation

var = AffiliationVariation(
    original_text="HC*EBSERH",
    normalized_text="Hospital das Clínicas - EBSERH",
    institution="HC-UFPE",
    platform="PubMed"
)
```

### 2. **Article**
Representa artigos coletados.

```python
from database.models import Article

article = Article(
    title="Título do Artigo",
    authors="Autor 1, Autor 2",
    doi="10.1234/example",
    platform="Scielo",
    publication_date="2024-01-15",
    abstract="Resumo do artigo...",
    url="https://example.com",
    status="VALIDADO"  # NOVO, VALIDADO, REJEITADO
)
```

### 3. **SearchHistory**
Registro de buscas realizadas.

```python
from database.models import SearchHistory

search = SearchHistory(
    search_term="Polifarmácia idosos",
    platforms="Scielo,PubMed",
    date_start="2024-01-01",
    date_end="2024-12-31",
    results_count=45
)
```

### 4. **ErrorLog**
Registro de erros e falhas.

```python
from database.models import ErrorLog

error = ErrorLog(
    error_type="Rejeição de Conteúdo",
    search_term="HC-UFPE",
    article_title="Título do artigo",
    article_doi="10.1234/error",
    platform="Lilacs",
    error_reason="Artigo fora do período configurado"
)
```

---

## 🔧 Como Usar o CRUD

### Conexão com o Banco

#### Opção 1: Context Manager (Recomendado)
```python
from database.db_manager import DatabaseManager

with DatabaseManager() as db:
    # Seu código aqui
    variations = db.read_all_affiliation_variations()
# Conexão fechada automaticamente
```

#### Opção 2: Instância Direta
```python
from database.db_manager import get_db

db = get_db()
try:
    variations = db.read_all_affiliation_variations()
finally:
    db.close()
```

---

## 🎯 Operações CRUD

### **AFFILIATION VARIATIONS**

#### CREATE
```python
from database.models import AffiliationVariation
from database.db_manager import get_db

var = AffiliationVariation(
    original_text="HC*UFPE",
    normalized_text="Hospital das Clínicas - UFPE",
    institution="HC-UFPE",
    platform="PubMed"
)

db = get_db()
variation_id = db.create_affiliation_variation(var)
print(f"Criado com ID: {variation_id}")
```

#### READ (Único)
```python
db = get_db()
variation = db.read_affiliation_variation(1)
print(variation)
```

#### READ (Todos)
```python
db = get_db()
all_variations = db.read_all_affiliation_variations()
for v in all_variations:
    print(v)
```

#### READ (Filtrado por Instituição)
```python
db = get_db()
hc_variations = db.read_affiliation_variations_by_institution("HC-UFPE")
for v in hc_variations:
    print(v)
```

#### UPDATE
```python
db = get_db()
variation = db.read_affiliation_variation(1)
variation.normalized_text = "Novo texto normalizado"
success = db.update_affiliation_variation(variation)
print(f"Atualizado: {success}")
```

#### DELETE
```python
db = get_db()
success = db.delete_affiliation_variation(1)
print(f"Deletado: {success}")
```

---

### **ARTICLES**

#### CREATE
```python
from database.models import Article
from database.db_manager import get_db

article = Article(
    title="Novo Artigo",
    authors="Autor 1",
    doi="10.1234/new",
    platform="PubMed",
    abstract="Resumo...",
    status="NOVO"
)

db = get_db()
article_id = db.create_article(article)
```

#### READ (por Status)
```python
db = get_db()
validated = db.read_articles_by_status("VALIDADO")
for article in validated:
    print(f"  - {article.title}")

new_articles = db.read_articles_by_status("NOVO")
rejected = db.read_articles_by_status("REJEITADO")
```

#### UPDATE (Status)
```python
db = get_db()
success = db.update_article_status(5, "VALIDADO")
print(f"Status atualizado: {success}")
```

---

### **SEARCH HISTORY**

#### CREATE
```python
from database.models import SearchHistory
from database.db_manager import get_db

search = SearchHistory(
    search_term="Inflamação",
    platforms="Scielo,PubMed",
    date_start="2024-01-01",
    date_end="2024-12-31",
    results_count=150
)

db = get_db()
search_id = db.create_search_history(search)
```

#### READ
```python
db = get_db()
history = db.read_search_history(limit=50)
for search in history:
    print(f"  - '{search.search_term}' ({search.results_count} resultados)")
```

---

### **ERROR LOGS**

#### CREATE
```python
from database.models import ErrorLog
from database.db_manager import get_db

error = ErrorLog(
    error_type="Erro de Conexão",
    search_term="HC-UFPE",
    platform="PubMed",
    error_reason="Timeout na conexão"
)

db = get_db()
error_id = db.create_error_log(error)
```

#### READ
```python
db = get_db()
errors = db.read_error_logs(limit=50)
for error in errors:
    print(f"  - {error.error_type}: {error.error_reason}")
```

---

## 📊 Estatísticas

```python
from database.db_manager import get_db

db = get_db()
stats = db.get_stats()

print(f"Variações: {stats['affiliation_variations']}")
print(f"Artigos: {stats['articles_total']}")
print(f"Validados: {stats['articles_validated']}")
print(f"Buscas: {stats['searches']}")
print(f"Erros: {stats['errors']}")
```

---

## 🔍 Queries Avançadas

Use a classe `SearchQueries` para queries complexas:

```python
from database.queries import SearchQueries, QueryBuilder
from database.db_manager import get_db

db = get_db()
cursor = db.connection.cursor()

# Contar artigos por status
query = SearchQueries.ARTICLES_COUNT_BY_STATUS
cursor.execute(query)
results = cursor.fetchall()

# Construir filtro dinâmico
query, params = QueryBuilder.build_articles_filter(
    platform="PubMed",
    status="VALIDADO",
    date_start="2024-01-01"
)
cursor.execute(query, params)
results = cursor.fetchall()
```

---

## 🧪 Executar Testes

```bash
python -m database.test_crud
```

Isso executará:
- Testes de Affiliation Variations
- Testes de Articles
- Testes de Search History
- Testes de Error Logs
- Estatísticas Gerais

---

## 💾 Estrutura do Banco de Dados

### Tabelas Criadas Automaticamente

```sql
-- Variações de Afiliação
CREATE TABLE affiliation_variations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_text TEXT NOT NULL,
    normalized_text TEXT NOT NULL,
    institution TEXT NOT NULL,
    platform TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- Artigos
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    authors TEXT,
    doi TEXT,
    platform TEXT NOT NULL,
    publication_date TEXT,
    abstract TEXT,
    url TEXT,
    status TEXT DEFAULT 'NOVO',
    collected_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- Histórico de Buscas
CREATE TABLE search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_term TEXT NOT NULL,
    platforms TEXT,
    date_start TEXT,
    date_end TEXT,
    results_count INTEGER DEFAULT 0,
    search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- Histórico de Erros
CREATE TABLE error_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    error_type TEXT NOT NULL,
    search_term TEXT,
    article_title TEXT,
    article_doi TEXT,
    platform TEXT,
    error_reason TEXT,
    error_date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

---

## ⚠️ Funções Perigosas

```python
# Limpar TODA a base de dados (Use com cuidado!)
db.clear_database()

# Deletar histórico antigo (via query)
from database.queries import SearchQueries
cursor.execute(SearchQueries.DELETE_OLD_SEARCH_HISTORY)
cursor.execute(SearchQueries.DELETE_OLD_ERROR_LOGS)
db.connection.commit()
```

---

## 🚀 Próximos Passos

1. **Integração com PubMed**: Implementar coleta de dados
2. **Integração com Interface**: Conectar GUI aos métodos CRUD
3. **Queries Avançadas**: Usar SearchQueries para filtros complexos
4. **Testes Unitários**: Expander test_crud.py

---

## 📝 Exemplo Completo

```python
from database.db_manager import DatabaseManager
from database.models import AffiliationVariation, Article, ErrorLog

# Usar com context manager
with DatabaseManager() as db:
    # Criar variação de afiliação
    var = AffiliationVariation(
        original_text="HC*UFPE",
        normalized_text="Hospital das Clínicas - UFPE",
        institution="HC-UFPE",
        platform="PubMed"
    )
    var_id = db.create_affiliation_variation(var)
    
    # Criar artigo
    article = Article(
        title="Estudo sobre HC-UFPE",
        authors="Silva, A.",
        platform="PubMed",
        status="NOVO"
    )
    art_id = db.create_article(article)
    
    # Registrar erro
    error = ErrorLog(
        error_type="Validação",
        article_title=article.title,
        error_reason="Rejeição por relevância"
    )
    err_id = db.create_error_log(error)
    
    # Ler estatísticas
    stats = db.get_stats()
    print(f"Total de artigos: {stats['articles_total']}")
    
# Conexão fechada automaticamente
```

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte os exemplos em `database/test_crud.py`
2. Revise a documentação de cada método
3. Verifique os comentários no código-fonte

