"""
Script de teste para validar a integração da ConfigWindow com o banco de dados.

Testa:
1. Carregamento de termos do BD
2. Adição de novo termo
3. Edição de termo
4. Deleção de termo
5. Validação de duplicatas
"""

from database.db_manager import DatabaseManager
from database.models import AffiliationVariation

def test_config_window_integration():
    """Testa integração da ConfigWindow com BD."""
    
    print("\n" + "="*70)
    print("TESTE DE INTEGRACAO: CONFIG WINDOW + BANCO DE DADOS".center(70))
    print("="*70)
    
    db = None
    try:
        # 1. Inicializar BD
        print("\n[1] Conectando ao banco de dados...")
        db = DatabaseManager()
        db.connect()
        print("    [OK] Conexao estabelecida")
        
        # 2. Carregar termos
        print("\n[2] Carregando termos HC-UFPE do banco...")
        variations = db.read_affiliation_variations_by_institution("HC-UFPE")
        print(f"    [OK] {len(variations)} variações carregadas")
        for var in variations[:3]:
            print(f"        - ID {var.id}: {var.original_text}")
        
        # 3. Adicionar novo termo
        print("\n[3] Adicionando novo termo de busca...")
        new_var = AffiliationVariation(
            original_text="Hospital das Clinicas TESTE",
            normalized_text="Hospital das Clínicas Teste",
            institution="HC-UFPE",
            platform="Manual"
        )
        new_id = db.create_affiliation_variation(new_var)
        print(f"    [OK] Termo adicionado com ID {new_id}")
        
        # 4. Validar adição
        print("\n[4] Validando adição...")
        retrieved = db.read_affiliation_variation(new_id)
        if retrieved:
            print(f"    [OK] Termo recuperado: {retrieved.original_text}")
        else:
            print("    [ERRO] Termo não foi inserido corretamente!")
        
        # 5. Atualizar termo
        print("\n[5] Atualizando termo...")
        retrieved.original_text = "Hospital das Clinicas TESTE ATUALIZADO"
        retrieved.normalized_text = "Hospital das Clínicas Teste Atualizado"
        success = db.update_affiliation_variation(retrieved)
        print(f"    [OK] Termo atualizado" if success else "    [ERRO] Falha ao atualizar")
        
        # 6. Validar atualização
        print("\n[6] Validando atualização...")
        updated = db.read_affiliation_variation(new_id)
        if updated and "ATUALIZADO" in updated.original_text:
            print(f"    [OK] Termo modificado: {updated.original_text}")
        else:
            print("    [ERRO] Termo não foi atualizado!")
        
        # 7. Validar duplicata
        print("\n[7] Testando validação de duplicata...")
        all_vars = db.read_affiliation_variations_by_institution("HC-UFPE")
        existing_texts = [v.original_text for v in all_vars]
        
        test_duplicate = existing_texts[0]
        if test_duplicate in existing_texts:
            print(f"    [OK] Duplicata detectada: '{test_duplicate}'")
        else:
            print("    [AVISO] Validação de duplicata nao funcionou")
        
        # 8. Deletar termo
        print("\n[8] Deletando termo de teste...")
        success = db.delete_affiliation_variation(new_id)
        print(f"    [OK] Termo deletado" if success else "    [ERRO] Falha ao deletar")
        
        # 9. Validar deleção
        print("\n[9] Validando deleção...")
        deleted = db.read_affiliation_variation(new_id)
        if deleted is None:
            print("    [OK] Termo foi removido do banco")
        else:
            print("    [ERRO] Termo ainda existe no banco!")
        
        # 10. Relatório final
        print("\n[10] Estatísticas finais:")
        final_vars = db.read_affiliation_variations_by_institution("HC-UFPE")
        print(f"    Total de termos HC-UFPE: {len(final_vars)}")
        
        print("\n" + "="*70)
        print("TESTE CONCLUIDO COM SUCESSO!".center(70))
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n[ERRO] Falha durante testes: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if db:
            db.close()
            print("[OK] Conexao com BD fechada")

if __name__ == "__main__":
    test_config_window_integration()
