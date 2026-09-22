import type { ModelOption } from "@/types";

const TIER_ORDER = ["fast", "balanced", "frontier"];

export function CostComparison({ alternatives, selectedId }: { alternatives: ModelOption[]; selectedId: string }) {
  const sorted = [...alternatives].sort((a, b) => TIER_ORDER.indexOf(a.tier) - TIER_ORDER.indexOf(b.tier));
  const maxCost = Math.max(...sorted.map((m) => m.estimated_cost_usd), 0.000001);

  return (
    <div className="space-y-2.5">
      {sorted.map((m) => {
        const pct = Math.max((m.estimated_cost_usd / maxCost) * 100, 4);
        const isSelected = m.id === selectedId;
        return (
          <div key={m.id} className="space-y-1">
            <div className="flex items-center justify-between text-xs">
              <span className={isSelected ? "font-semibold text-foreground" : "text-muted-foreground"}>
                {m.name} {isSelected && "← selected"}
              </span>
              <span className="font-mono text-muted-foreground">${m.estimated_cost_usd.toFixed(6)}</span>
            </div>
            <div className="h-2.5 w-full overflow-hidden rounded-full bg-muted">
              <div
                className="h-full rounded-full transition-all"
                style={{
                  width: `${pct}%`,
                  backgroundColor: isSelected ? "var(--color-primary)" : "color-mix(in oklab, var(--color-primary) 35%, transparent)",
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
