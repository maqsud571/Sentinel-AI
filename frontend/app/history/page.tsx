import Link from "next/link";
import { getHistory } from "@/lib/api";

export default async function HistoryPage() {
  const history = await getHistory();

  return (
    <div className="stack">
      <section className="page-heading">
        <div>
          <p className="eyebrow">Scan tarixi</p>
          <h1>History</h1>
        </div>
      </section>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Target</th>
              <th>Status</th>
              <th>Score</th>
              <th>Findings</th>
              <th>Sana</th>
            </tr>
          </thead>
          <tbody>
            {history.map((item) => (
              <tr key={item.id}>
                <td>
                  <Link href={`/scan/${item.id}`}>{item.target}</Link>
                </td>
                <td>{item.status}</td>
                <td>{item.score}</td>
                <td>{item.findings_count}</td>
                <td>{new Date(item.created_at).toLocaleString()}</td>
              </tr>
            ))}
            {history.length === 0 && (
              <tr>
                <td colSpan={5}>Tarix hozircha bo'sh.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

