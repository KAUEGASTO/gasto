// Gastô · função "lembrete" (Supabase Edge Function)
// Manda a notificação "Lançou seus gastos?" para os celulares que ativaram os lembretes.
//  - {mode:"cron"}  + cabeçalho x-cron: CRON_SECRET  -> todos os celulares (chamado às 13:30 e 21:00)
//  - {mode:"test"}  + login do app (Authorization)    -> só os celulares de quem pediu o teste
// Segredos (Edge Functions → Secrets): VAPID_PUBLIC, VAPID_PRIVATE, CRON_SECRET
import webpush from "npm:web-push@3.6.7";
import { createClient } from "npm:@supabase/supabase-js@2";

const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
webpush.setVapidDetails("https://gastoapp.github.io", Deno.env.get("VAPID_PUBLIC")!, Deno.env.get("VAPID_PRIVATE")!);
const CORS = { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "authorization, apikey, content-type, x-cron", "Access-Control-Allow-Methods": "POST, OPTIONS" };
const out = (o: unknown, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { ...CORS, "Content-Type": "application/json" } });
const money = (v: number) => "R$ " + v.toFixed(2).replace(".", ",").replace(/\B(?=(\d{3})+(?!\d))/g, ".");

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  let body: { mode?: string } = {};
  try { body = await req.json(); } catch { /* vazio */ }

  let q = sb.from("push_subs").select("endpoint,sub,user_id,family_id");
  if (body.mode === "test") {
    const jwt = (req.headers.get("authorization") || "").replace(/^Bearer\s+/i, "");
    const { data, error } = await sb.auth.getUser(jwt);
    if (error || !data.user) return out({ error: "login inválido" }, 401);
    q = q.eq("user_id", data.user.id);
  } else if (req.headers.get("x-cron") !== Deno.env.get("CRON_SECRET")) {
    return out({ error: "não autorizado" }, 401);
  }
  const { data: subs, error } = await q;
  if (error) return out({ error: error.message }, 500);

  // hoje no horário de Brasília
  const today = new Date(Date.now() - 3 * 3600e3).toISOString().slice(0, 10);
  const hour = new Date(Date.now() - 3 * 3600e3).getUTCHours();
  const cache = new Map<string, string>();
  let sent = 0, gone = 0, failed = 0, err = "";
  for (const s of subs || []) {
    // quem é essa pessoa no app e o que ela já lançou hoje
    let text = cache.get(s.user_id + s.family_id);
    if (!text) {
      const { data: m } = await sb.from("members").select("person_id").eq("family_id", s.family_id).eq("user_id", s.user_id).maybeSingle();
      const { data: ex } = await sb.from("items").select("data").eq("family_id", s.family_id).eq("kind", "expense").eq("deleted", false).eq("data->>date", today);
      const mine = (ex || []).map((r) => r.data).filter((d) => !m?.person_id || d.who === m.person_id);
      const tot = mine.reduce((a, d) => a + (Number(d.total) || 0), 0);
      text = mine.length
        ? `Hoje você lançou ${mine.length} ${mine.length === 1 ? "gasto" : "gastos"} (${money(tot)}). Faltou algum?`
        : hour < 17 ? "Nenhum gasto seu lançado hoje ainda. Comprou algo? Lança rapidinho." : "Nenhum gasto seu lançado hoje. Comprou algo? Lança antes de esquecer.";
      cache.set(s.user_id + s.family_id, text);
    }
    const payload = JSON.stringify({ title: body.mode === "test" ? "Gastô · teste" : "Lançou seus gastos?", body: text, url: "./#novo" });
    try { await webpush.sendNotification(s.sub, payload, { TTL: 3600, urgency: "high" }); sent++; }
    catch (e) {
      const code = (e as { statusCode?: number }).statusCode;
      if (code === 404 || code === 410) { await sb.from("push_subs").delete().eq("endpoint", s.endpoint); gone++; } else { failed++; err = String((e as Error).message || e).slice(0, 200); }
    }
  }
  return out({ sent, gone, failed, err });
});
