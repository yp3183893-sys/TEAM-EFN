import { useEffect, useMemo, useRef, useState } from "react";

function classNames(...xs) {
  return xs.filter(Boolean).join(" ");
}

function LogoMark() {
  return (
    <div className="flex items-center gap-2">
      <div className="grid h-9 w-9 place-items-center rounded-xl bg-emerald-600 text-white shadow-sm">
        <span className="text-lg font-semibold">A</span>
      </div>
      <div className="leading-tight">
        <div className="text-sm font-semibold text-white">AgroCapital</div>
        <div className="text-xs text-white/70">AgriTech AI · Créditos FIRA</div>
      </div>
    </div>
  );
}

function SectionTitle({ eyebrow, title, subtitle }) {
  return (
    <div className="mx-auto max-w-2xl text-center">
      {eyebrow ? (
        <div className="text-xs font-semibold uppercase tracking-wider text-emerald-300">
          {eyebrow}
        </div>
      ) : null}
      <h2 className="mt-2 text-2xl font-semibold tracking-tight text-white sm:text-3xl">
        {title}
      </h2>
      {subtitle ? (
        <p className="mt-3 text-sm leading-6 text-white/70 sm:text-base">
          {subtitle}
        </p>
      ) : null}
    </div>
  );
}

function FeatureCard({ step, title, description }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-sm backdrop-blur">
      <div className="flex items-center justify-between">
        <div className="inline-flex items-center rounded-full bg-emerald-500/15 px-3 py-1 text-xs font-semibold text-emerald-200">
          Paso {step}
        </div>
        <div className="h-8 w-8 rounded-xl bg-white/5" />
      </div>
      <h3 className="mt-4 text-base font-semibold text-white">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-white/70">{description}</p>
    </div>
  );
}

function ChatBubble({ role, text, meta }) {
  const isUser = role === "user";
  return (
    <div className={classNames("flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={classNames(
          "max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-6 shadow-sm",
          isUser
            ? "bg-emerald-600 text-white"
            : "border border-white/10 bg-white/5 text-white"
        )}
      >
        <div className="whitespace-pre-wrap">{text}</div>
        {meta ? (
          <div
            className={classNames(
              "mt-2 text-[11px]",
              isUser ? "text-white/80" : "text-white/60"
            )}
          >
            {meta}
          </div>
        ) : null}
      </div>
    </div>
  );
}

function mockAgentReply(userText) {
  const t = (userText || "").toLowerCase();

  if (t.includes("hola") || t.includes("buenas")) {
    return (
      "¡Hola! Soy AgroCapital.\n" +
      "Te precalifico para un crédito FIRA en minutos. Para iniciar:\n" +
      "1) ¿En qué estado/municipio estás?\n" +
      "2) ¿Cuántas hectáreas trabajas? (ej. 120 ha)"
    );
  }

  const haMatch = t.match(/(\d+(?:[.,]\d+)?)\s*(ha|hectareas|hectáreas)\b/);
  if (haMatch) {
    const ha = Number(String(haMatch[1]).replace(",", "."));
    if (!Number.isNaN(ha)) {
      const tier = ha >= 300 ? "alta" : ha >= 80 ? "media" : "inicial";
      return (
        `Perfecto: ${ha} ha.\n` +
        `Precalificación estimada: ${tier.toUpperCase()}.\n` +
        "Ahora dime:\n" +
        "- ¿Qué cultivo principal trabajas?\n" +
        "- ¿El crédito es para capital de trabajo o maquinaria?"
      );
    }
  }

  if (t.includes("maquinaria") || t.includes("tractor")) {
    return (
      "Entendido: maquinaria.\n" +
      "Para precalificar, necesito:\n" +
      "- Monto estimado (MXN)\n" +
      "- Antigüedad del negocio (años)\n" +
      "- ¿Tienes historial de crédito? (sí/no)"
    );
  }

  if (t.includes("capital") || t.includes("insumos") || t.includes("fertiliz")) {
    return (
      "Entendido: capital de trabajo/insumos.\n" +
      "Para precalificar rápido:\n" +
      "- Monto estimado (MXN)\n" +
      "- Ventas promedio por ciclo\n" +
      "- ¿Cuentas con contrato de venta/cliente ancla? (sí/no)"
    );
  }

  if (t.includes("crm") || t.includes("hubspot")) {
    return "Listo: cuando confirmes tus datos, registro el lead automáticamente en HubSpot para que un asesor te contacte.";
  }

  return (
    "Gracias. Para continuar con la precalificación FIRA:\n" +
    "1) Ubicación (estado/municipio)\n" +
    "2) Hectáreas\n" +
    "3) Tipo de crédito (maquinaria o capital de trabajo)"
  );
}

async function sendToBackend(text) {
  const res = await fetch("/api/webhook", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      channel: "webhook",
      sender_phone: "+520000000000",
      sender_name: "Demo Web",
      text
    })
  });
  if (!res.ok) {
    throw new Error("Backend error");
  }
  return res.json();
}

export default function App() {
  const chatRef = useRef(null);
  const listRef = useRef(null);

  const [draft, setDraft] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [messages, setMessages] = useState(() => [
    {
      id: crypto.randomUUID(),
      role: "agent",
      text:
        "Soy AgroCapital, tu agente de IA para créditos agrícolas.\n" +
        "Escríbeme como si fuera WhatsApp y te precalifico al instante.",
      meta: "Agente · 24/7"
    }
  ]);

  const quickPrompts = useMemo(
    () => [
      "Hola, quiero un crédito FIRA",
      "Trabajo 120 ha de maíz",
      "Necesito crédito para maquinaria (tractor)",
      "Busco capital de trabajo para fertilizantes"
    ],
    []
  );

  useEffect(() => {
    if (!listRef.current) return;
    listRef.current.scrollTop = listRef.current.scrollHeight;
  }, [messages, isTyping]);

  function scrollToChat() {
    chatRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  async function sendMessage(text) {
    const content = (text ?? "").trim();
    if (!content) return;

    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: "user", text: content, meta: "Productor" }
    ]);
    setDraft("");
    setIsTyping(true);

    try {
      // Para conectar tu backend FastAPI:
      // - Si corres con Docker Compose, esto ya funciona vía proxy:
      //   Frontend (5173) -> /api -> Backend (8000)
      // - Si lo quieres sin proxy, cambia fetch("/api/webhook") por "http://localhost:8000/webhook"
      const data = await sendToBackend(content);
      const reply = data?.reply || mockAgentReply(content);

      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "agent",
          text: reply,
          meta: `Agente · intent=${data?.intent ?? "mock"} · score=${Math.round(
            (data?.lead_score ?? 0) * 100
          )}%`
        }
      ]);
    } catch {
      const reply = mockAgentReply(content);
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "agent",
          text: reply,
          meta: "Agente · modo mock"
        }
      ]);
    } finally {
      setIsTyping(false);
    }
  }

  function onSubmit(e) {
    e.preventDefault();
    sendMessage(draft);
  }

  return (
    <div className="min-h-screen bg-neutral-950 text-white">
      <div className="absolute inset-x-0 top-0 -z-10 h-[520px] bg-gradient-to-b from-emerald-900/40 via-emerald-950/10 to-transparent" />

      <header className="sticky top-0 z-20 border-b border-white/10 bg-neutral-950/70 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6">
          <LogoMark />
          <div className="flex items-center gap-2">
            <a
              href="#como-funciona"
              className="hidden rounded-lg px-3 py-2 text-sm text-white/80 hover:bg-white/5 hover:text-white sm:inline-block"
            >
              Cómo funciona
            </a>
            <button
              onClick={scrollToChat}
              className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-emerald-500 active:bg-emerald-700"
            >
              Probar demo
            </button>
          </div>
        </div>
      </header>

      <main>
        <section className="mx-auto max-w-6xl px-4 pb-10 pt-14 sm:px-6 sm:pb-16 sm:pt-20">
          <div className="grid items-center gap-10 lg:grid-cols-2">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-white/70">
                <span className="h-2 w-2 rounded-full bg-emerald-400" />
                WhatsApp · Precalificación · HubSpot
              </div>

              <h1 className="mt-4 text-3xl font-semibold tracking-tight sm:text-5xl">
                Acelera tus créditos agrícolas con IA
              </h1>
              <p className="mt-4 max-w-xl text-sm leading-6 text-white/70 sm:text-base">
                AgroCapital atiende 24/7 por WhatsApp, precalifica productores con reglas tipo FIRA al instante
                y registra automáticamente el lead en HubSpot para tu equipo comercial.
              </p>

              <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center">
                <button
                  onClick={scrollToChat}
                  className="rounded-xl bg-emerald-600 px-5 py-3 text-sm font-semibold text-white shadow-sm hover:bg-emerald-500 active:bg-emerald-700"
                >
                  Probar demo
                </button>
                <a
                  href="#como-funciona"
                  className="rounded-xl border border-white/10 bg-white/5 px-5 py-3 text-sm font-semibold text-white hover:bg-white/10"
                >
                  Ver cómo funciona
                </a>
              </div>

              <div className="mt-6 grid grid-cols-3 gap-3 max-w-xl">
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <div className="text-xs text-white/60">Respuesta</div>
                  <div className="mt-1 text-lg font-semibold">24/7</div>
                </div>
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <div className="text-xs text-white/60">Tiempo</div>
                  <div className="mt-1 text-lg font-semibold">&lt; 2 min</div>
                </div>
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <div className="text-xs text-white/60">CRM</div>
                  <div className="mt-1 text-lg font-semibold">HubSpot</div>
                </div>
              </div>
            </div>

            <div className="relative">
              <div className="rounded-3xl border border-white/10 bg-white/5 p-5 shadow-sm backdrop-blur">
                <div className="flex items-center justify-between">
                  <div className="text-sm font-semibold">Vista previa</div>
                  <div className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-white/70">
                    AgriTech UI
                  </div>
                </div>
                <div className="mt-4 rounded-2xl border border-white/10 bg-neutral-950/40 p-4">
                  <div className="space-y-3">
                    <ChatBubble
                      role="agent"
                      text="¿Cuántas hectáreas trabajas y qué cultivo principal produces?"
                      meta="Agente"
                    />
                    <ChatBubble role="user" text="Trabajo 120 ha de maíz" meta="Productor" />
                    <ChatBubble
                      role="agent"
                      text="Precalificación estimada: MEDIA. ¿Crédito para maquinaria o capital de trabajo?"
                      meta="Agente"
                    />
                  </div>
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  {quickPrompts.map((p) => (
                    <button
                      key={p}
                      onClick={() => sendMessage(p)}
                      className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-white/80 hover:bg-white/10"
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>

              <div className="pointer-events-none absolute -right-6 -top-8 h-40 w-40 rounded-full bg-emerald-500/20 blur-3xl" />
              <div className="pointer-events-none absolute -bottom-10 -left-8 h-44 w-44 rounded-full bg-white/10 blur-3xl" />
            </div>
          </div>
        </section>

        <section id="como-funciona" className="border-t border-white/10">
          <div className="mx-auto max-w-6xl px-4 py-14 sm:px-6 sm:py-16">
            <SectionTitle
              eyebrow="Cómo funciona"
              title="3 pasos para convertir conversaciones en leads listos"
              subtitle="Reduce fricción comercial: captura por WhatsApp, precalifica y deja el prospecto listo para el asesor."
            />

            <div className="mt-10 grid gap-4 md:grid-cols-3">
              <FeatureCard
                step="1"
                title="El productor escribe por WhatsApp"
                description="El agente atiende al instante y captura datos clave con una conversación natural."
              />
              <FeatureCard
                step="2"
                title="IA precalifica según reglas tipo FIRA"
                description="Evalúa señales como hectáreas, propósito del crédito e información operativa básica."
              />
              <FeatureCard
                step="3"
                title="Se guarda el lead en el CRM"
                description="Se inyecta el contacto automáticamente en HubSpot para seguimiento por asesores."
              />
            </div>
          </div>
        </section>

        <section ref={chatRef} className="border-t border-white/10">
          <div className="mx-auto max-w-6xl px-4 py-14 sm:px-6 sm:py-16">
            <SectionTitle
              eyebrow="Demo interactiva"
              title="Simulación de chat estilo WhatsApp"
              subtitle="Escribe un mensaje y mira cómo el agente responde. Si el backend está arriba, responde real vía /webhook."
            />

            <div className="mx-auto mt-10 max-w-3xl overflow-hidden rounded-3xl border border-white/10 bg-white/5 shadow-sm backdrop-blur">
              <div className="flex items-center justify-between border-b border-white/10 bg-neutral-950/40 px-5 py-4">
                <div>
                  <div className="text-sm font-semibold text-white">AgroCapital · Demo</div>
                  <div className="text-xs text-white/60">Atención 24/7 · Precalificación · HubSpot</div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-emerald-400" />
                  <div className="text-xs text-white/70">Online</div>
                </div>
              </div>

              <div ref={listRef} className="h-[360px] space-y-3 overflow-y-auto px-5 py-5 sm:h-[420px]">
                {messages.map((m) => (
                  <ChatBubble key={m.id} role={m.role} text={m.text} meta={m.meta} />
                ))}

                {isTyping ? (
                  <div className="flex justify-start">
                    <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/70">
                      AgroCapital está escribiendo…
                    </div>
                  </div>
                ) : null}
              </div>

              <div className="border-t border-white/10 bg-neutral-950/40 p-4">
                <form onSubmit={onSubmit} className="flex items-center gap-3">
                  <input
                    value={draft}
                    onChange={(e) => setDraft(e.target.value)}
                    placeholder='Ej: "Trabajo 120 ha y necesito crédito para maquinaria"'
                    className="w-full rounded-2xl border border-white/10 bg-neutral-950/60 px-4 py-3 text-sm text-white placeholder:text-white/40 outline-none focus:border-emerald-500/60"
                  />
                  <button
                    type="submit"
                    className="rounded-2xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white hover:bg-emerald-500 active:bg-emerald-700 disabled:opacity-60"
                    disabled={!draft.trim() || isTyping}
                  >
                    Enviar
                  </button>
                </form>

                <div className="mt-3 flex flex-wrap gap-2">
                  {quickPrompts.map((p) => (
                    <button
                      key={p}
                      type="button"
                      onClick={() => sendMessage(p)}
                      className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-white/80 hover:bg-white/10"
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="mx-auto mt-6 max-w-3xl rounded-2xl border border-white/10 bg-white/5 p-5 text-sm text-white/70">
              Tip: si el backend no está disponible, la demo responde en modo mock automáticamente.
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-white/10">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 px-4 py-10 text-sm text-white/60 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <div>Equipo TEAM-EFN · AgroCapital</div>
          <div>© {new Date().getFullYear()} Todos los derechos reservados.</div>
        </div>
      </footer>
    </div>
  );
}

