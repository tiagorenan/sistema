## 🚀 CHEAT SHEET - CRUD NEXUS PESQUISA

*Referência rápida de como usar o CRUD*

---

## ⚡ Setup Rápido

```python
from database import DatabaseManager, AffiliationVariation, Article

# Opção 1: Context Manager (Recomendado)
with DatabaseManager() as db:
    db.create_article(...)

# Opção 2: Instância
db = DatabaseManager()
try:
    db.create_article(...)
finally:
    db.close()
```

---

## 📝 Operações Rápidas

### CRIAR
```python
# Variação
var = AffiliationVariation(
    original_text="HC*UFPE",
    normalized_text="Hospital das Clínicas - UFPE",
    institution="HC-UFPE",
    platform="PubMed"
)
var_id = db.create_affiliation_variation(var)

# Artigo
article = Article(
    title="Título",
    authors="Autor 1",
    platform="PubMed",
    status="NOVO"
)
art_id = db.create_article(article)
```

### LER
```python
# Uma variação
var = db.read_affiliation_variation(1)

# Todas as variações
all_vars = db.read_all_affiliation_variations()

# Variações de uma instituição
hc_vars = db.read_affiliation_variations_by_institution("HC-UFPE")

# Artigos por status
validated = db.read_articles_by_status("VALIDADO")
new_articles = db.read_articles_by_status("NOVO")

# Histórico de buscas
history = db.read_search_history(limit=50)

# Logs de erro
errors = db.read_error_logs(limit=50)
```

### ATUALIZAR
```python
# Variação
var = db.read_affiliation_variation(1)
var.normalized_text = "Novo texto"
db.update_affiliation_variation(var)

# Status do artigo
db.update_article_status(5, "VALIDADO")
```

### DELETAR
```python
db.delete_affiliation_variation(1)
```

---

## 📊 Estatísticas
```python
stats = db.get_stats()
print(f"Artigos: {stats['articles_total']}")
print(f"Validados: {stats['articles_validated']}")
print(f"Buscas: {stats['searches']}")
print(f"Erros: {stats['errors']}")
```

---

## 🔍 Filtros Avançados
```python
from database.queries import QueryBuilder

query, params = QueryBuilder.build_articles_filter(
    platform="PubMed",
    status="VALIDADO",
    date_start="2024-01-01"
)

cursor = db.connection.cursor()
cursor.execute(query, params)
results = cursor.fetchall()
```

---

## 📚 Arquivo de Banco
- **Localização**: `nexus_pesquisa.db`
- **Tipo**: SQLite3
- **Tabelas**: 4
  - `affiliation_variations`
  - `articles`
  - `search_history`
  - `error_logs`

---

## 🧪 Testar
```bash
python -m database.test_crud
```

---

## 📖 Mais Informações
- `DATABASE_CRUD_GUIDE.md` - Documentação completa
- `CRUD_SUMMARY.md` - Resumo da implementação
- `database/example_pubmed_integration.py` - Exemplos

