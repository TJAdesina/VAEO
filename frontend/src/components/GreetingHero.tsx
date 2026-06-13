import { motion } from "framer-motion";

export default function GreetingHero({ greeting, subtitle }: { greeting: string; subtitle: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="text-center mt-6 mb-8"
    >
      <div className="mx-auto w-16 h-16 rounded-full bg-sage-light/40 flex items-center justify-center mb-4">
        <span className="text-2xl">🌾</span>
      </div>
      <h1 className="font-display text-[22px] font-semibold text-soil leading-tight">{greeting}</h1>
      <p className="mt-3 text-soil-light text-[15px] leading-relaxed max-w-md mx-auto">{subtitle}</p>
    </motion.div>
  );
}
