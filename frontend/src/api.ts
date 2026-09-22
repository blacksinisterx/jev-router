import type { CatalogModel, DemoTask, RoutingResult, TaskRequest } from "./types";

const BASE = "/api";

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

export const routeTask = (task: TaskRequest) =>
  fetch(`${BASE}/route`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(task),
  }).then((r) => json<RoutingResult>(r));

export const getDecisions = () => fetch(`${BASE}/decisions`).then((r) => json<RoutingResult[]>(r));

export const getExamples = () => fetch(`${BASE}/examples`).then((r) => json<DemoTask[]>(r));

export const getCatalog = () => fetch(`${BASE}/catalog`).then((r) => json<CatalogModel[]>(r));
