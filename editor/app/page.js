'use client';

import { useEffect, useMemo, useState } from 'react';
import './style.css';

export default function Editor() {
  const [units, setUnits] = useState([]);
  const [query, setQuery] = useState('');
  const [selectedId, setSelectedId] = useState('');
  const [bororo, setBororo] = useState('');
  const [portuguese, setPortuguese] = useState('');
  const [pending, setPending] = useState({});

  useEffect(() => {
    fetch('/api/units').then(r => {
      if (!r.ok) throw new Error('Não foi possível carregar o corpus.');
      return r.json();
    }).then(data => {
      setUnits(data);
      if (data.length) select(data[0], {});
    }).catch(console.error);
    const saved = localStorage.getItem('corbo-editor-pending');
    if (saved) setPending(JSON.parse(saved));
  }, []);

  function select(unit, pendingState = pending) {
    setSelectedId(unit.id);
    const edit = pendingState[unit.id];
    setBororo(edit?.bororo ?? unit.bororo ?? '');
    setPortuguese(edit?.portuguese ?? unit.portuguese ?? '');
  }

  const selected = units.find(u => u.id === selectedId);
  const filtered = useMemo(() => {
    const q = query.trim().toLocaleLowerCase('pt-BR');
    if (!q) return units;
    return units.filter(u => `${u.id} ${u.bororo} ${u.portuguese}`.toLocaleLowerCase('pt-BR').includes(q));
  }, [units, query]);

  function register() {
    if (!selected) return;
    const next = {...pending, [selected.id]: {
      id: selected.id,
      original_bororo: selected.bororo ?? '',
      original_portuguese: selected.portuguese ?? '',
      bororo,
      portuguese,
      recorded_at: new Date().toISOString()
    }};
    setPending(next);
    localStorage.setItem('corbo-editor-pending', JSON.stringify(next));
  }

  function cancel() {
    if (!selected) return;
    const edit = pending[selected.id];
    setBororo(edit?.bororo ?? selected.bororo ?? '');
    setPortuguese(edit?.portuguese ?? selected.portuguese ?? '');
  }

  return <main>
    <header><div><div className="eyebrow">CORBO · ÁREA EDITORIAL</div><h1>Editor do corpus</h1></div><div className="private">Acesso privado</div></header>
    <div className="layout">
      <aside>
        <input className="search" value={query} onChange={e=>setQuery(e.target.value)} placeholder="ID ou texto…" />
        <div className="count">{filtered.length} unidades</div>
        <nav className="units">{filtered.map(u => <button key={u.id} className={u.id===selectedId?'active':''} onClick={()=>select(u)}><span>{u.id}</span><small>{u.bororo}</small>{pending[u.id] && <b>alteração pendente</b>}</button>)}</nav>
      </aside>
      <section className="editor">
        {!selected ? <p>Carregando…</p> : <>
          <div className="unithead"><div><span className="label">Unidade</span><strong>{selected.id}</strong></div>{pending[selected.id] && <span className="badge">alteração pendente</span>}</div>
          <div className="original"><span className="label">Texto publicado</span><p className="bororo">{selected.bororo}</p><p>{selected.portuguese}</p></div>
          <label><span>Bororo revisado</span><textarea value={bororo} onChange={e=>setBororo(e.target.value)} /></label>
          <label><span>Português revisado</span><textarea value={portuguese} onChange={e=>setPortuguese(e.target.value)} /></label>
          <div className="actions"><button className="secondary" onClick={cancel}>Cancelar</button><button className="primary" onClick={register}>Registrar correção</button></div>
          <p className="notice">Registrar uma correção cria uma alteração editorial pendente no navegador. Não modifica o corpus publicado. A gravação no TSV canônico será habilitada somente pelo endpoint autenticado.</p>
        </>}
      </section>
    </div>
  </main>;
}
