import { NewScanForm } from "@/components/NewScanForm";

export default function NewScanPage() {
  return (
    <div className="stack narrow">
      <section className="page-heading">
        <div>
          <p className="eyebrow">Target qo'shish</p>
          <h1>Yangi xavfsizlik skani</h1>
        </div>
      </section>
      <NewScanForm />
    </div>
  );
}

