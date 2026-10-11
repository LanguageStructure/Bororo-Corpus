# Vocabulário temático: revisão e publicação

A interface pública está em `docs/vocabulario-tematico.html` e lê apenas `docs/data/vocabulario-tematico-publico.json`.

**Nunca adicionar arquivos privados de fauna ou etnobotânica ao repositório, inclusive em commits antigos, testes, exemplos ou histórico.** Não copiar suas entradas para a página pública sem autorização específica.

## Fluxo de revisão

1. Preparar **fora do repositório** uma planilha CSV com as colunas `bororo,portugues,tema,publicar,fonte_publica`.
2. Verificar a forma Bororo, o significado em português e uma fonte **já pública** que sustente a publicação. Uma tradução de sentença não é evidência suficiente de tradução lexical.
3. Marcar `publicar=sim` **somente** para entradas expressamente autorizadas; demais linhas ficam vazias ou com `não`.
4. Executar localmente `python3 scripts/export_approved_vocabulary.py /caminho/privado/revisao.csv`.
5. Revisar o diff de `docs/data/vocabulario-tematico-publico.json` antes de fazer commit apenas desse arquivo.

Temas válidos: Fauna; Flora e etnobotânica; Corpo humano; Cores; Parentesco; Verbos e ações; Alimentação; Território e natureza.

**Estado atual:** nenhuma entrada autorizada publicada. As categorias e atividades já estão disponíveis, mas não há palavras até a conclusão da revisão.

Para obter vocabulário do dicionário, localizar uma fonte lexical pública verificável e revisar as equivalências; não gerar definições automaticamente a partir do índice de lemas ou de traduções livres.
