// Vocabulário de apresentação em português; não modifica as etiquetas CoNLL-U.
window.CorBoUDpt={
  "upos": {
    "ADJ": "adjetivo",
    "ADP": "adposição",
    "ADV": "advérbio",
    "AUX": "auxiliar",
    "CCONJ": "conjunção coordenativa",
    "DET": "determinante",
    "INTJ": "interjeição",
    "NOUN": "substantivo",
    "NUM": "numeral",
    "PART": "partícula",
    "PRON": "pronome",
    "PROPN": "nome próprio",
    "PUNCT": "pontuação",
    "SCONJ": "conjunção subordinativa",
    "SYM": "símbolo",
    "VERB": "verbo",
    "X": "outra classe"
  },
  "features": {
    "Person": {
      "1": "1ª pessoa",
      "2": "2ª pessoa",
      "3": "3ª pessoa"
    },
    "Number": {
      "Sing": "singular",
      "Plur": "plural",
      "Dual": "dual"
    },
    "Tense": {
      "Past": "passado",
      "Pres": "presente",
      "Fut": "futuro"
    },
    "Mood": {
      "Ind": "indicativo",
      "Imp": "imperativo",
      "Sub": "subjuntivo",
      "Cnd": "condicional",
      "Pot": "potencial"
    },
    "VerbForm": {
      "Fin": "finito",
      "Inf": "infinitivo",
      "Ger": "gerúndio",
      "Part": "particípio"
    },
    "Polarity": {
      "Neg": "negativo",
      "Pos": "positivo"
    },
    "Voice": {
      "Pass": "passiva",
      "Act": "ativa"
    },
    "Case": {
      "Nom": "nominativo",
      "Acc": "acusativo",
      "Gen": "genitivo",
      "Dat": "dativo",
      "Loc": "locativo",
      "Abl": "ablativo",
      "Ins": "instrumental"
    },
    "PronType": {
      "Prs": "pessoal",
      "Dem": "demonstrativo",
      "Int": "interrogativo",
      "Rel": "relativo"
    },
    "Speech": {
      "Quo": "discurso citado"
    }
  }
};
window.CorBoUDpt.classe=function(x){return this.upos[x]||x||''};
window.CorBoUDpt.tracos=function(s){if(!s||s==='_')return '';return String(s).split('|').map(p=>{const [k,v]=p.split('=');return (this.features[k]&&this.features[k][v])||p}).join(' · ')};
