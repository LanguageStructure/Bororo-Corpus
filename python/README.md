# corbo-tokenizer

Tokenizador do Bororo (Boe, `bor`) com a mesma lógica da página **Tokenizador** do CorBo:
separa palavras e pontuação e, no modo linguístico, devolve a segmentação morfológica
registrada no inventário v5 (`docs/data/tokenizer-v5-site.json`), com o estado de revisão
(`confirmed`, `proposed`, `proposed_low_support`, `unanalysed`).

```bash
pip install ./python            # a partir da raiz do repositório
corbo-tokenize "Boe egore aekugigire."
corbo-tokenize --format conllu < texto.txt
```

```python
from corbo_tokenizer import Tokenizer
tk = Tokenizer()                # procura o inventário no repositório ou baixa do site
for t in tk.analyze("Boe egore aekugigire."):
    print(t.form, t.segments, t.status)
```

O inventário é lido de, nesta ordem: o argumento `inventory=`, a variável de ambiente
`CORBO_INVENTORY`, `docs/data/tokenizer-v5-site.json` no repositório, ou o site publicado.
Análises `proposed` não são verificadas; veja `docs/TOKENIZER.md`.
