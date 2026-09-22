import { Cpu, Gauge, Zap } from "lucide-react";
import { cn } from "@/lib/utils";

const TIER_CONFIG = {
  fast: { label: "Fast", icon: Zap, classes: "bg-sky-500/10 text-sky-600 dark:text-sky-400 border-sky-500/30" },
  balanced: { label: "Balanced", icon: Gauge, classes: "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/30" },
  frontier: { label: "Frontier", icon: Cpu, classes: "bg-indigo-600/10 text-indigo-700 dark:text-indigo-400 border-indigo-600/30" },
} as const;

export function ModelBadge({ tier, name, className }: { tier: keyof typeof TIER_CONFIG; name?: string; className?: string }) {
  const { label, icon: Icon, classes } = TIER_CONFIG[tier];
  return (
    <span className={cn("inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold", classes, className)}>
      <Icon className="size-3.5" />
      {name ?? label}
    </span>
  );
}
