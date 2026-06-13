export default function DiagnosticProgress({ step, total = 3 }: { step: number; total?: number }) {
  return (
    <div className="flex items-center gap-1.5 mt-1 text-xs text-soil-light">
      {Array.from({ length: total }).map((_, i) => (
        <span
          key={i}
          className={`w-1.5 h-1.5 rounded-full ${i < step ? "bg-sage" : "bg-cream-border"}`}
        />
      ))}
      <span className="ml-1">
        Question {step} of {total}
      </span>
    </div>
  );
}
