import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "ingestao"))

from classificador import classificar_ticket


def test_classifica_bug_critico():
    texto = "O sistema caiu em produção, ninguém consegue acessar!"
    resultado = classificar_ticket(texto)
    assert resultado["categoria"] == "bug"
    assert resultado["urgencia"] == "critica"


def test_classifica_duvida_padrao():
    texto = "Como eu troco minha senha de acesso?"
    resultado = classificar_ticket(texto)
    assert resultado["categoria"] == "duvida"
    assert resultado["urgencia"] == "media"


def test_classifica_reclamacao():
    texto = "Estou muito insatisfeito com o atendimento, quero cancelar"
    resultado = classificar_ticket(texto)
    assert resultado["categoria"] == "reclamacao"


if __name__ == "__main__":
    test_classifica_bug_critico()
    print("✅ Bug crítico")
    test_classifica_duvida_padrao()
    print("✅ Dúvida padrão")
    test_classifica_reclamacao()
    print("✅ Reclamação")