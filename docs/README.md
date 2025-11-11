# 📚 Documentação - NEXUS Pesquisa

## Organização da Documentação

Esta pasta contém toda a documentação do projeto NEXUS Pesquisa, organizada por tópico.

---

## 📋 Índice de Arquivos

### 🎯 Visão Geral do Projeto
- **[README.md](README.md)** - Este arquivo (índice)
- **[PROGRESSO.md](PROGRESSO.md)** - Status geral e progresso da Sprint 2
- **[SUMARIO_EXECUTIVO.md](SUMARIO_EXECUTIVO.md)** - Resumo executivo das entregas

### 🔧 Integração ConfigWindow + Banco de Dados
- **[INTEGRACAO_CONFIG_WINDOW.md](INTEGRACAO_CONFIG_WINDOW.md)** - Documentação técnica completa
- **[RESUMO_CONFIG_WINDOW.md](RESUMO_CONFIG_WINDOW.md)** - Visão geral simplificada
- **[GUIA_USO_CONFIG_WINDOW.md](GUIA_USO_CONFIG_WINDOW.md)** - Guia do usuário (como usar)
- **[CHECKLIST_CONFIG_BD.md](CHECKLIST_CONFIG_BD.md)** - Checklist das mudanças implementadas

### 🗂️ Especificações e Implementação
- **[TERMOS_PADRAO_IMPLEMENTACAO.md](TERMOS_PADRAO_IMPLEMENTACAO.md)** - Documentação dos 20 termos HC-UFPE
- **[PUBMED_IMPLEMENTATION_GUIDE.md](PUBMED_IMPLEMENTATION_GUIDE.md)** - Guia para implementar PubMed Collector
- **[DATABASE_CRUD_GUIDE.md](DATABASE_CRUD_GUIDE.md)** - Guia de operações CRUD

### 📖 Resumos e Checklists
- **[CRUD_SUMMARY.md](CRUD_SUMMARY.md)** - Resumo das operações CRUD
- **[CRUD_CHEATSHEET.md](CRUD_CHEATSHEET.md)** - Referência rápida de CRUD

---

## 🎯 Começar Aqui

### Para Usuários
1. Leia: **[GUIA_USO_CONFIG_WINDOW.md](GUIA_USO_CONFIG_WINDOW.md)**
2. Abra a aplicação: `python __main__.py`
3. Teste as funcionalidades

### Para Desenvolvedores
1. Leia: **[SUMARIO_EXECUTIVO.md](SUMARIO_EXECUTIVO.md)**
2. Estude: **[INTEGRACAO_CONFIG_WINDOW.md](INTEGRACAO_CONFIG_WINDOW.md)**
3. Verifique: **[DATABASE_CRUD_GUIDE.md](DATABASE_CRUD_GUIDE.md)**
4. Implemente: **[PUBMED_IMPLEMENTATION_GUIDE.md](PUBMED_IMPLEMENTATION_GUIDE.md)**

### Para Gestores/Stakeholders
1. Leia: **[SUMARIO_EXECUTIVO.md](SUMARIO_EXECUTIVO.md)**
2. Verifique: **[PROGRESSO.md](PROGRESSO.md)**
3. Acompanhe: Métricas e status

---

## 📊 Status Sprint 2

```
Sprint 2: 5/8 COMPLETO (62.5%)

✅ CRUD Database
✅ Docker Preparation
✅ Default Search Terms (22 variações)
✅ ConfigWindow Integration ⭐
⏳ PubMed Collector (Próximo)
⏳ Full GUI Integration
⏳ Reporting/Export
```

---

## 🧪 Testes

### Testes Passando ✅
```
CRUD Tests:           6/6 ✅
Integration Tests:    10/10 ✅
Visual Tests:         ✅
```

### Como Rodar Testes
```powershell
# CRUD Tests
python -m database.test_crud

# Integration Tests
python test_config_integration.py

# Aplicação
python __main__.py
```

---

## 📁 Estrutura do Projeto

```
nexus_pesquisa/
├── docs/                          ← VOCÊ ESTÁ AQUI
│   ├── README.md
│   ├── PROGRESSO.md
│   ├── SUMARIO_EXECUTIVO.md
│   ├── INTEGRACAO_CONFIG_WINDOW.md
│   ├── RESUMO_CONFIG_WINDOW.md
│   ├── GUIA_USO_CONFIG_WINDOW.md
│   ├── CHECKLIST_CONFIG_BD.md
│   └── ... (mais arquivos)
│
├── Interface/
│   ├── config_window.py           ✅ Integrada com BD
│   ├── main_window.py
│   ├── results_window.py
│   └── ...
│
├── database/
│   ├── db_manager.py              ✅ CRUD 13 ops
│   ├── models.py
│   ├── seed_data.py               ✅ 22 termos
│   ├── test_crud.py               ✅ 6/6 testes
│   └── ...
│
├── processing/
│   ├── search_helper.py           ✅ 3 funções
│   ├── collectors/
│   │   └── pubmed.py              ⏳ Próximo
│   └── ...
│
├── config.py                      ✅ DATABASE_URL support
├── __main__.py
├── nexus_pesquisa.db              (BD SQLite)
└── test_config_integration.py     ✅ 10/10 testes
```

---

## 🚀 Próximos Passos

### Priority 1: PubMed Collector (Task 5)
Implementar `processing/collectors/pubmed.py`
- Usar termos da ConfigWindow
- Integrar com API PubMed
- Coletar artigos com afiliação HC

### Priority 2: Full GUI Integration (Task 6)
Conectar todas as 5 janelas
- Sincronizar dados em tempo real
- Fluxo completo: Search → Results → History

### Priority 3: Reporting/Export (Task 7)
Implementar exports
- PDF/Excel
- Gráficos
- Relatórios

---

## 📞 Contato & Suporte

- **Desenvolvedor:** Tiago Renan
- **Email:** tiago.renan@ufpe.br
- **Repositório:** [GitHub](https://github.com/tiagorenan/sistema)
- **Documentação:** Esta pasta

---

## 📈 Métricas

| Métrica | Valor |
|---------|-------|
| Sprint 2 Progresso | 5/8 (62.5%) ✅ |
| CRUD Operations | 13 ✅ |
| Database Tables | 4 ✅ |
| Search Terms | 22 ✅ |
| CRUD Tests | 6/6 ✅ |
| Integration Tests | 10/10 ✅ |
| Documentação | 8+ arquivos ✅ |

---

## 📅 Changelog

### Novembro 10, 2025
- ✅ ConfigWindow integrada com BD
- ✅ CRUD completo testado
- ✅ 22 termos gerenciáveis
- ✅ Documentação completa criada
- ✅ Unicode encoding corrigido

---

**Última atualização:** 10 de Novembro de 2025  
**Status:** ✅ Pronto para Produção  
**Próximo Review:** Após implementação do PubMed Collector
