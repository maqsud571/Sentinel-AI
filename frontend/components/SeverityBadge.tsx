import type { Finding } from "@/lib/api";

const classes: Record<Finding["severity"], string> = {
  Info: "sev sev-info",
  Low: "sev sev-low",
  Medium: "sev sev-medium",
  High: "sev sev-high",
  Critical: "sev sev-critical",
};

export function SeverityBadge({ severity }: { severity: Finding["severity"] }) {
  return <span className={classes[severity]}>{severity}</span>;
}

