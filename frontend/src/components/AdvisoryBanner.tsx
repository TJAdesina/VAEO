import { motion } from "framer-motion";
import { X } from "lucide-react";

export default function AdvisoryBanner({
  label,
  message,
  onSwitch,
  onDismiss,
}: {
  label: string;
  message: string;
  onSwitch: () => void;
  onDismiss: () => void;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      className="bg-gold/25 border-b border-gold/40 px-4 py-2.5"
    >
      <div className="mx-auto max-w-conv flex items-center gap-3">
        <p className="text-sm text-soil flex-1">{message}</p>
        <button
          onClick={onSwitch}
          className="text-sm font-medium bg-soil text-cream rounded-full px-3 py-1.5"
        >
          {label}
        </button>
        <button onClick={onDismiss} className="tap flex items-center justify-center text-soil-light">
          <X size={18} />
        </button>
      </div>
    </motion.div>
  );
}
