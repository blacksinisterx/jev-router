import { useEffect, useMemo, useState } from "react";
import { Loader2, Moon, Route, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { ModelBadge } from "@/components/model-badge";
import { StatTile } from "@/components/stat-tile";
import { CostComparison } from "@/components/cost-comparison";
import { useTheme } from "@/lib/use-theme";
import { getCatalog, getDecisions, getExamples, routeTask } from "./api";
import type { CatalogModel, DemoTask, RoutingResult } from "./types";

function ThemeToggle() {
  const { theme, toggle } = useTheme();
  return (
    <Button variant="outline" size="icon" onClick={toggle} aria-label="Toggle theme">
      {theme === "dark" ? <Sun className="size-4" /> : <Moon className="size-4" />}
    </Button>
  );
}

function ResultCard({ result }: { result: RoutingResult }) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Routing decision</CardTitle>
          <ModelBadge tier={result.selected_model.tier} />
        </div>
        <CardDescription>Routed to {result.selected_model.name} via Jev ({result.provider})</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm">{result.reason}</p>

        <dl className="grid grid-cols-3 gap-3 text-xs">
          <div>
            <dt className="text-muted-foreground">Jev latency</dt>
            <dd className="font-mono text-foreground">{result.latency_ms.toFixed(2)} ms</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Est. cost</dt>
            <dd className="font-mono text-foreground">${result.selected_model.estimated_cost_usd.toFixed(6)}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Est. model latency</dt>
            <dd className="font-mono text-foreground">{result.selected_model.estimated_latency_ms.toFixed(0)} ms</dd>
          </div>
        </dl>

        <div>
          <p className="mb-2 text-xs font-medium text-muted-foreground">Cost across catalog for this prompt</p>
          <CostComparison alternatives={result.alternatives} selectedId={result.selected_model.id} />
        </div>

        {Object.keys(result.raw_answers).length > 0 && (
          <Accordion type="single" collapsible>
            <AccordionItem value="raw" className="border-none">
              <AccordionTrigger className="text-xs text-muted-foreground">Raw Jev answers</AccordionTrigger>
              <AccordionContent>
                <pre className="overflow-x-auto rounded-md bg-muted p-3 text-xs">
                  {JSON.stringify(result.raw_answers, null, 2)}
                </pre>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        )}
      </CardContent>
    </Card>
  );
}

export default function App() {
  const [examples, setExamples] = useState<DemoTask[]>([]);
  const [catalog, setCatalog] = useState<CatalogModel[]>([]);
  const [decisions, setDecisions] = useState<RoutingResult[]>([]);
  const [result, setResult] = useState<RoutingResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [provider, setProvider] = useState<string>("mock");
  const [prompt, setPrompt] = useState("");

  useEffect(() => {
    getExamples().then(setExamples).catch(() => {});
    getCatalog().then(setCatalog).catch(() => {});
    getDecisions().then(setDecisions).catch(() => {});
    fetch("/api/health").then((r) => r.json()).then((d) => setProvider(d.provider)).catch(() => {});
  }, []);

  const grouped = useMemo(
    () =>
      examples.reduce<Record<string, DemoTask[]>>((acc, ex) => {
        (acc[ex.category] ??= []).push(ex);
        return acc;
      }, {}),
    [examples],
  );
  const categories = Object.keys(grouped);
  const [activeCategory, setActiveCategory] = useState<string>("");
  useEffect(() => {
    if (!activeCategory && categories.length > 0) setActiveCategory(categories[0]);
  }, [categories, activeCategory]);

  async function runTask(text: string) {
    setLoading(true);
    setError(null);
    try {
      const res = await routeTask({ prompt: text });
      setResult(res);
      setDecisions((prev) => [res, ...prev].slice(0, 50));
    } catch (e) {
      setError(e instanceof Error ? e.message : "routing failed");
    } finally {
      setLoading(false);
    }
  }

  const stats = useMemo(() => {
    const total = decisions.length;
    const totalCost = decisions.reduce((s, d) => s + d.selected_model.estimated_cost_usd, 0);
    const avgLatency = total ? decisions.reduce((s, d) => s + d.latency_ms, 0) / total : 0;
    const tierCounts: Record<string, number> = {};
    for (const d of decisions) tierCounts[d.selected_model.tier] = (tierCounts[d.selected_model.tier] ?? 0) + 1;
    const topTier = Object.entries(tierCounts).sort((a, b) => b[1] - a[1])[0]?.[0] ?? "—";
    return { total, totalCost, avgLatency, topTier };
  }, [decisions]);

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="border-b">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2.5">
            <Route className="size-6 text-primary" />
            <div>
              <h1 className="text-lg font-semibold leading-tight">JevRouter</h1>
              <p className="text-xs text-muted-foreground">An intelligent LLM model router</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="rounded-full border px-2.5 py-1 font-mono text-xs text-muted-foreground">
              provider: {provider}
            </span>
            <ThemeToggle />
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl space-y-6 px-6 py-8">
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <StatTile label="Requests routed" value={String(stats.total)} />
          <StatTile label="Total est. cost" value={`$${stats.totalCost.toFixed(6)}`} />
          <StatTile label="Avg Jev latency" value={`${stats.avgLatency.toFixed(1)} ms`} />
          <StatTile label="Most-used tier" value={stats.topTier} />
        </div>

        <div className="grid gap-6 lg:grid-cols-5">
          <div className="space-y-6 lg:col-span-3">
            <Card>
              <CardHeader>
                <CardTitle>Try a demo task</CardTitle>
                <CardDescription>Different task shapes route to different model tiers.</CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs value={activeCategory} onValueChange={setActiveCategory}>
                  <TabsList className="mb-3 h-auto flex-wrap">
                    {categories.map((c) => (
                      <TabsTrigger key={c} value={c} className="text-xs">
                        {c}
                      </TabsTrigger>
                    ))}
                  </TabsList>
                  {categories.map((c) => (
                    <TabsContent key={c} value={c} className="flex flex-col gap-2">
                      {grouped[c].map((ex, i) => (
                        <button
                          key={i}
                          onClick={() => runTask(ex.prompt)}
                          disabled={loading}
                          className="rounded-md border bg-card px-3 py-2 text-left text-xs transition-colors hover:bg-accent hover:text-accent-foreground disabled:opacity-50"
                        >
                          {ex.prompt}
                        </button>
                      ))}
                    </TabsContent>
                  ))}
                </Tabs>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Or propose your own task</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="space-y-1.5">
                  <Label htmlFor="prompt">Prompt</Label>
                  <Textarea id="prompt" rows={4} value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="Describe the task you'd send to a model..." />
                </div>
                <Button onClick={() => runTask(prompt)} disabled={loading || !prompt.trim()} className="w-full">
                  {loading && <Loader2 className="size-4 animate-spin" />}
                  Route
                </Button>
                {error && <p className="text-sm text-critical">{error}</p>}
              </CardContent>
            </Card>

            {catalog.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Model catalog</CardTitle>
                  <CardDescription>Illustrative pricing/latency — not live-fetched from any provider.</CardDescription>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Model</TableHead>
                        <TableHead>Tier</TableHead>
                        <TableHead>$/M in</TableHead>
                        <TableHead>$/M out</TableHead>
                        <TableHead>Avg latency</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {catalog.map((m) => (
                        <TableRow key={m.id}>
                          <TableCell className="text-xs">{m.name}</TableCell>
                          <TableCell>
                            <ModelBadge tier={m.tier as "fast" | "balanced" | "frontier"} />
                          </TableCell>
                          <TableCell className="font-mono text-xs">${m.input_price_per_m.toFixed(2)}</TableCell>
                          <TableCell className="font-mono text-xs">${m.output_price_per_m.toFixed(2)}</TableCell>
                          <TableCell className="font-mono text-xs text-muted-foreground">{m.avg_latency_ms.toFixed(0)}ms</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            )}
          </div>

          <div className="lg:col-span-2">
            {result ? (
              <ResultCard result={result} />
            ) : (
              <Card className="flex h-full min-h-48 items-center justify-center text-sm text-muted-foreground">
                Run a demo task to see a routing decision here.
              </Card>
            )}
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Recent decisions</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Prompt</TableHead>
                  <TableHead>Model</TableHead>
                  <TableHead>Tier</TableHead>
                  <TableHead>Cost</TableHead>
                  <TableHead>Jev latency</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {decisions.map((d, i) => (
                  <TableRow key={i}>
                    <TableCell className="max-w-xs truncate text-xs">{d.prompt}</TableCell>
                    <TableCell className="text-xs">{d.selected_model.name}</TableCell>
                    <TableCell>
                      <ModelBadge tier={d.selected_model.tier} />
                    </TableCell>
                    <TableCell className="font-mono text-xs">${d.selected_model.estimated_cost_usd.toFixed(6)}</TableCell>
                    <TableCell className="font-mono text-xs text-muted-foreground">{d.latency_ms.toFixed(1)}ms</TableCell>
                  </TableRow>
                ))}
                {decisions.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5} className="py-8 text-center text-muted-foreground">
                      No decisions yet — try a demo task.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
