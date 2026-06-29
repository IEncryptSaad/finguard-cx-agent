'use client';
import { FormEvent, useState } from 'react';
import { sendChat } from '@/lib/api';
type Msg = { role: 'customer' | 'agent'; text: string };
export function ChatShell() {
  const [messages, setMessages] = useState<Msg[]>([{ role: 'agent', text: 'Hi, I am FinGuard. How can I help with your account or support request?' }]);
  const [input, setInput] = useState('');
  const [conversationId, setConversationId] = useState<string>();
  const [loading, setLoading] = useState(false);
  async function onSubmit(e: FormEvent) {
    e.preventDefault(); if (!input.trim()) return;
    const text = input.trim(); setInput(''); setMessages((m) => [...m, { role: 'customer', text }]); setLoading(true);
    try { const res = await sendChat(text, conversationId); setConversationId(res.conversation_id); setMessages((m) => [...m, { role: 'agent', text: `${res.message}${res.handoff_required ? ' A human specialist has been notified.' : ''}` }]); }
    catch { setMessages((m) => [...m, { role: 'agent', text: 'Sorry, the support service is unavailable.' }]); }
    finally { setLoading(false); }
  }
  return <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4 shadow-xl"><div className="mb-4 h-96 space-y-3 overflow-y-auto rounded-xl bg-slate-950/70 p-4">{messages.map((m,i)=><div key={i} className={m.role==='agent'?'text-left':'text-right'}><span className={`inline-block max-w-[80%] rounded-2xl px-4 py-2 ${m.role==='agent'?'bg-slate-800':'bg-brand-600'}`}>{m.text}</span></div>)}{loading && <p className="text-sm text-slate-400">FinGuard is thinking…</p>}</div><form onSubmit={onSubmit} className="flex gap-2"><input className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-brand-600" value={input} onChange={(e)=>setInput(e.target.value)} placeholder="Ask about a transaction, card, dispute, or account issue"/><button className="rounded-xl bg-brand-600 px-5 py-3 font-semibold hover:bg-blue-500">Send</button></form></section>;
}
