export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const SERVER_API_BASE = process.env.INTERNAL_API_BASE_URL ?? API_BASE;

export type Scan = {
  id: string;
  target: string;
  normalized_target: string;
  status: "queued" | "running" | "analyzing" | "completed" | "failed";
  score: number;
  summary?: string | null;
  error?: string | null;
  scanner_meta?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type Finding = {
  id: number;
  title: string;
  severity: "Info" | "Low" | "Medium" | "High" | "Critical";
  category: string;
  evidence?: string | null;
  recommendation?: string | null;
  details: Record<string, unknown>;
};

export type ScanResult = Scan & {
  findings: Finding[];
};

export type HistoryItem = {
  id: string;
  target: string;
  status: Scan["status"];
  score: number;
  findings_count: number;
  created_at: string;
};

export async function getHistory(): Promise<HistoryItem[]> {
  const response = await fetch(`${SERVER_API_BASE}/history`, { cache: "no-store" });
  if (!response.ok) return [];
  return response.json();
}

export async function getScanResult(id: string): Promise<ScanResult> {
  const response = await fetch(`${API_BASE}/results/${id}`, { cache: "no-store" });
  if (!response.ok) throw new Error("Scan natijasini olishda xatolik.");
  return response.json();
}

export function reportUrl(id: string): string {
  return `${API_BASE}/report/${id}`;
}
