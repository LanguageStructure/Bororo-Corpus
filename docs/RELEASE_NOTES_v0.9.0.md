# CorBo v0.9.0 — notas de lançamento (rascunho)

**Estado:** preparação; ainda não publicado.

## Escopo
- Atualização do corpus CoNLL-U a partir do arquivo de trabalho de 17 de outubro de 2026.
- Reconstrução dos índices públicos do corpus, do modelo lexical do tokenizador e do índice gramatical.
- Preservação das análises linguísticas manuais e das fontes documentais.
- Revisões humanas e anotações editoriais não são equivalentes a validação independente.

## Limitações conhecidas
- O corpus permanece parcialmente anotado. A presença de um token ou de um `sent_id` não implica que a análise esteja completa.
- Alguns blocos de sentença ainda precisam de revisão estrutural (blocos sem `sent_id` e blocos com mais de um `sent_id`).
- O tokenizador é um modelo conservador baseado nas formas e análises atestadas; candidatas de segmentação **não são** análises morfológicas validadas nem estimativas de acurácia.
- Diferenças de lema ou UPOS podem refletir polissemia, funções sintáticas distintas ou decisões de anotação ainda em revisão.

## Procedimento antes da publicação
1. Executar `python3 scripts/stage_conllu_release.py /caminho/para/corbo_fix.conllu`.
2. Conferir o relatório `CorBo_vNext/annotations/latest_conllu_import_report.json`.
3. Conferir `git status`, `git diff --stat` e a saída dos três construtores.
4. Verificar manualmente as páginas públicas de corpus, morfologia, UD e tokenizador.
5. Confirmar que os artefatos derivados correspondem ao SHA-256 do arquivo importado.
6. Só então fazer commit/push, criar a tag `v0.9.0`, publicar o release no GitHub e verificar a sincronização com o Zenodo.

**Atenção:** não usar este rascunho como prova de que a publicação já ocorreu.
