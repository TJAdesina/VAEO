export default function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 px-4 py-2 self-start bg-white border border-cream-border rounded-bubble rounded-bl-sm shadow-soft">
      <Dot delay="0s" />
      <Dot delay="0.15s" />
      <Dot delay="0.3s" />
    </div>
  );
}

function Dot({ delay }: { delay: string }) {
  return (
    <span
      className="w-1.5 h-1.5 rounded-full bg-sage inline-block"
      style={{ animation: `pulse 1s ${delay} infinite`, opacity: 0.5 }}
    />
  );
}
