import { ScanResultView } from "@/components/ScanResultView";

export default async function ScanPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <ScanResultView id={id} />;
}
