export const API_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');
export type User = { user_id: number; full_name: string; email: string; role: string };
export function getToken() { return typeof window === 'undefined' ? null : localStorage.getItem('skillbridge_token'); }
export function saveSession(token: string, user?: User) { localStorage.setItem('skillbridge_token', token); if (user) localStorage.setItem('skillbridge_user', JSON.stringify(user)); }
export function clearSession() { localStorage.removeItem('skillbridge_token'); localStorage.removeItem('skillbridge_user'); }
export async function api<T = any>(path: string, options: RequestInit = {}): Promise<T> {
 const headers = new Headers(options.headers); const token = getToken(); if (token) headers.set('Authorization', `Bearer ${token}`); if (options.body && !(options.body instanceof FormData)) headers.set('Content-Type','application/json');
 let response: Response; try { response = await fetch(`${API_URL}${path}`, {...options,headers,cache:'no-store'}); } catch { throw new Error(`Cannot reach backend at ${API_URL}. Start FastAPI and check NEXT_PUBLIC_API_URL.`); }
 const raw = await response.text(); let data:any=null; try { data=raw?JSON.parse(raw):null; } catch { data=raw; }
 if(!response.ok){const d=data?.detail; const msg=Array.isArray(d)?d.map((x:any)=>`${x.loc?.join('.')}: ${x.msg}`).join('; '):d||data?.message||`Request failed (${response.status})`;throw new Error(msg);} return data as T;
}
export const asArray=(v:any):any[]=>Array.isArray(v)?v:Array.isArray(v?.items)?v.items:Array.isArray(v?.data)?v.data:Array.isArray(v?.recommendations)?v.recommendations:[];
export const money=(v:any)=>`₹${Number(v||0).toLocaleString('en-IN')}`;
