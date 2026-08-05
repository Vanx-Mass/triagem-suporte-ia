import re

# Palavras-chave por categoria — ordem importa: a primeira categoria
# que bater primeiro é a escolhida
REGRAS_CATEGORIA = [
    ("bug", [
        "não funciona", "nao funciona", "erro", "falha", "quebrado",
        "travando", "travou", "bug", "não abre", "nao abre", "caiu"
    ]),
    ("reclamacao", [
        "péssimo", "pessimo", "insatisfeito", "reclamação", "reclamacao",
        "cancelar", "decepcionado", "horrível", "horrivel"
    ]),
    ("solicitacao", [
        "gostaria de", "poderia adicionar", "solicito", "preciso de acesso",
        "quero solicitar", "por favor adicione"
    ]),
]

PALAVRAS_URGENCIA_CRITICA = [
    "produção", "producao", "sistema fora", "todos os usuários",
    "todos os usuarios", "parou tudo", "urgente", "crítico", "critico"
]

PALAVRAS_URGENCIA_ALTA = [
    "não consigo", "nao consigo", "bloqueado", "impedido", "hoje", "agora"
]


def classificar_ticket(texto: str) -> dict:
    """
    Classifica um ticket por correspondência de palavras-chave.

    Esta é uma implementação sem custo, pensada para portfólio sem
    orçamento para chamadas de LLM em produção. A interface é idêntica
    à de uma versão baseada em API (mesma assinatura de entrada/saída),
    então pode ser substituída por uma chamada real à Anthropic API ou
    outro provedor sem alterar nenhum outro ponto do sistema — ver
    DECISAO_ARQUITETURA.md.
    """
    texto_normalizado = texto.lower()

    categoria = _classificar_categoria(texto_normalizado)
    urgencia = _classificar_urgencia(texto_normalizado)

    return {"categoria": categoria, "urgencia": urgencia}


def _classificar_categoria(texto: str) -> str:
    for categoria, palavras in REGRAS_CATEGORIA:
        if any(palavra in texto for palavra in palavras):
            return categoria
    return "duvida"  # padrão quando nenhuma regra bate


def _classificar_urgencia(texto: str) -> str:
    if any(p in texto for p in PALAVRAS_URGENCIA_CRITICA):
        return "critica"
    if any(p in texto for p in PALAVRAS_URGENCIA_ALTA):
        return "alta"
    return "media"