#!/usr/bin/env python3
"""Metadados para buscadores e catálogos de dados.

  docs/sitemap.xml, docs/robots.txt   para indexação do site
  JSON-LD schema.org/Dataset           inserido em index.html e en.html
                                       (Google Dataset Search e similares)
  docs/olac.xml                        registro OLAC (repositório estático),
                                       pronto para cadastro em language-archives.org
"""
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BASE = "https://languagestructure.github.io/Bororo-Corpus/"
DOI = "10.5281/zenodo.12110451"  # DOI conceitual: resolve sempre para a versão mais recente
TODAY = date.today().isoformat()


def dataset():
    stats = {}
    p = DOCS / "data/statistics-summary.json"
    if p.exists():
        stats = json.loads(p.read_text(encoding="utf-8"))
    return {
        "@context": "https://schema.org", "@type": "Dataset",
        "name": "CorBo: Corpus da Língua Bororo (Bororo Language Corpus)",
        "alternateName": "CorBo",
        "description": ("Documentary corpus of Bororo (Boe, ISO 639-3 bor), Mato Grosso, Brazil: oral narratives, archival and "
                        "fieldwork texts, songs, biblical translations and dictionary materials, with Portuguese translations and "
                        "CoNLL-U annotation following Universal Dependencies. "
                        + (f"{stats.get('units', 0):,} documentary units, {stats.get('tokens', 0):,} tokens." if stats else "")),
        "url": BASE, "sameAs": [f"https://doi.org/{DOI}", "https://github.com/LanguageStructure/Bororo-Corpus"],
        "identifier": f"https://doi.org/{DOI}", "version": "0.10.1",
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "creator": {"@type": "Person", "name": "Fabrício Ferraz Gerardi", "identifier": "https://orcid.org/0000-0002-1438-7336"},
        "inLanguage": ["bor", "pt"],
        "keywords": ["Bororo", "Boe", "Bororoan", "language documentation", "parallel corpus", "CoNLL-U",
                     "Universal Dependencies", "Indigenous languages of Brazil"],
        "spatialCoverage": {"@type": "Place", "name": "Mato Grosso, Brazil"},
        "isAccessibleForFree": True, "dateModified": TODAY,
        "distribution": [
            {"@type": "DataDownload", "encodingFormat": "text/tab-separated-values", "contentUrl": BASE + "downloads/corbo-parallel.tsv"},
            {"@type": "DataDownload", "encodingFormat": "text/plain",
             "contentUrl": "https://raw.githubusercontent.com/LanguageStructure/Bororo-Corpus/main/CorBo/Corpus_Files/CorBo.conllu"},
        ],
    }


def inject(path, data):
    s = path.read_text(encoding="utf-8")
    block = '<script type="application/ld+json" id="dataset-jsonld">' + json.dumps(data, ensure_ascii=False) + "</script>"
    if 'id="dataset-jsonld"' in s:
        s = re.sub(r'<script type="application/ld\+json" id="dataset-jsonld">.*?</script>', lambda _: block, s, flags=re.S)
    else:
        s = s.replace("</head>", block + "</head>", 1) if "</head>" in s else s.replace("<title>", block + "<title>", 1)
    path.write_text(s, encoding="utf-8")


def main():
    data = dataset()
    for name in ("index.html", "en.html"):
        if (DOCS / name).exists():
            inject(DOCS / name, data)
    pages = sorted(p.name for p in DOCS.glob("*.html"))
    urls = "".join(f"<url><loc>{BASE}{'' if p == 'index.html' else p}</loc><lastmod>{TODAY}</lastmod></url>" for p in pages)
    (DOCS / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
                                      f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n', encoding="utf-8")
    (DOCS / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n", encoding="utf-8")
    olac = f"""<?xml version="1.0" encoding="UTF-8"?>
<Repository xmlns="http://www.openarchives.org/OAI/2.0/static-repository"
  xmlns:oai="http://www.openarchives.org/OAI/2.0/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/static-repository http://www.language-archives.org/OAI/2.0/static-repository.xsd">
 <Identify>
  <oai:repositoryName>CorBo: Corpus da Língua Bororo</oai:repositoryName>
  <oai:baseURL>http://www.language-archives.org/register/static/languagestructure.github.io/Bororo-Corpus/olac.xml</oai:baseURL>
  <oai:protocolVersion>2.0</oai:protocolVersion>
  <oai:adminEmail>A_PREENCHER@example.org</oai:adminEmail>
  <oai:earliestDatestamp>2026-01-01</oai:earliestDatestamp>
  <oai:deletedRecord>no</oai:deletedRecord>
  <oai:granularity>YYYY-MM-DD</oai:granularity>
  <oai:description>
   <olac-archive xmlns="http://www.language-archives.org/OLAC/1.1/olac-archive" type="institutional"
     currentAsOf="{TODAY}" xsi:schemaLocation="http://www.language-archives.org/OLAC/1.1/olac-archive http://www.language-archives.org/OLAC/1.1/olac-archive.xsd">
    <archiveURL>{BASE}</archiveURL>
    <participant name="Fabrício Ferraz Gerardi" role="Curator" email="A_PREENCHER@example.org"/>
    <institution>Boe eno moto</institution>
    <shortLocation>Mato Grosso, Brazil</shortLocation>
    <synopsis>Documentary and annotated corpus of Bororo (bor).</synopsis>
    <access>Open access under CC BY 4.0.</access>
   </olac-archive>
  </oai:description>
 </Identify>
 <ListMetadataFormats>
  <oai:metadataFormat><oai:metadataPrefix>olac</oai:metadataPrefix>
   <oai:schema>http://www.language-archives.org/OLAC/1.1/olac.xsd</oai:schema>
   <oai:metadataNamespace>http://www.language-archives.org/OLAC/1.1/</oai:metadataNamespace></oai:metadataFormat>
 </ListMetadataFormats>
 <ListRecords metadataPrefix="olac">
  <oai:record><oai:header><oai:identifier>oai:languagestructure.github.io:Bororo-Corpus</oai:identifier><oai:datestamp>{TODAY}</oai:datestamp></oai:header>
   <oai:metadata>
    <olac:olac xmlns:olac="http://www.language-archives.org/OLAC/1.1/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/"
      xsi:schemaLocation="http://www.language-archives.org/OLAC/1.1/ http://www.language-archives.org/OLAC/1.1/olac.xsd">
     <dc:title>CorBo: Corpus da Língua Bororo</dc:title>
     <dc:creator>Ferraz Gerardi, Fabrício</dc:creator>
     <dc:subject xsi:type="olac:language" olac:code="bor"/>
     <dc:language xsi:type="olac:language" olac:code="bor"/>
     <dc:language xsi:type="olac:language" olac:code="por"/>
     <dc:type xsi:type="olac:linguistic-type" olac:code="primary_text"/>
     <dc:type xsi:type="olac:linguistic-type" olac:code="language_description"/>
     <dc:type xsi:type="dcterms:DCMIType">Text</dc:type>
     <dc:description>{data['description']}</dc:description>
     <dc:identifier>https://doi.org/{DOI}</dc:identifier>
     <dc:identifier>{BASE}</dc:identifier>
     <dcterms:license>https://creativecommons.org/licenses/by/4.0/</dcterms:license>
     <dcterms:spatial>Mato Grosso, Brazil</dcterms:spatial>
    </olac:olac>
   </oai:metadata></oai:record>
 </ListRecords>
</Repository>
"""
    (DOCS / "olac.xml").write_text(olac, encoding="utf-8")
    print(f"sitemap com {len(pages)} páginas; JSON-LD em index.html e en.html; olac.xml")


if __name__ == "__main__":
    main()
