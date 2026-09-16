import { NextResponse } from 'next/server';

const OWNER = 'LanguageStructure';
const REPO = 'Bororo-Corpus';
const PATH = 'docs/data/coqueiro-units.json';

export async function GET() {
  const token = process.env.GITHUB_READ_TOKEN;
  const headers = { 'Accept': 'application/vnd.github.raw+json' };
  if (token) headers.Authorization = `Bearer ${token}`;
  const url = `https://api.github.com/repos/${OWNER}/${REPO}/contents/${PATH}?ref=main`;
  const response = await fetch(url, { headers, cache: 'no-store' });
  if (!response.ok) return NextResponse.json({error:'Corpus indisponível'}, {status:502});
  const data = await response.json();
  return NextResponse.json(data);
}
