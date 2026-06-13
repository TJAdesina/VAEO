import { motion } from "framer-motion";
import { Sprout, Bug, Mountain, Beef } from "lucide-react";

export default function TopicTiles({
  labels,
  onPick,
}: {
  labels: [string, string, string, string];
  onPick: (label: string) => void;
}) {
  const items = [
    { label: labels[0], icon: Sprout, tint: "bg-sage-light/30 text-sage-dark" },
    { label: labels[1], icon: Bug, tint: "bg-terracotta/15 text-terracotta" },
    { label: labels[2], icon: Mountain, tint: "bg-soil-light/15 text-soil" },
    { label: labels[3], icon: Beef, tint: "bg-gold/20 text-soil" },
  ];
  return (
    <div className="grid grid-cols-2 gap-3 mt-4">
      {items.map((it, i) => {
        const Icon = it.icon;
        return (
          <motion.button
            key={it.label}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + i * 0.05 }}
            whileTap={{ scale: 0.97 }}
            onClick={() => onPick(`I have a question about ${it.label.toLowerCase()}.`)}
            className="bg-white border border-cream-border rounded-2xl p-4 flex items-center gap-3 text-left shadow-soft hover:shadow-lift transition-shadow"
          >
            <span className={`w-10 h-10 rounded-xl flex items-center justify-center ${it.tint}`}>
              <Icon size={20} />
            </span>
            <span className="font-display font-semibold text-soil">{it.label}</span>
          </motion.button>
        );
      })}
    </div>
  );
}
