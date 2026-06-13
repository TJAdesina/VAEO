import { motion } from "framer-motion";
import clsx from "clsx";
import AudioReplayPill from "./AudioReplayPill";

export default function ChatBubble({
  role,
  text,
  streaming,
  language,
}: {
  role: "user" | "assistant";
  text: string;
  streaming?: boolean;
  language: string;
}) {
  const isUser = role === "user";
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={clsx("flex", isUser ? "justify-end" : "justify-start")}
    >
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-sage-light/60 flex items-center justify-center mr-2 mt-0.5 shrink-0">
          <span className="text-sm">👨🏾‍🌾</span>
        </div>
      )}
      <div className={clsx("max-w-[78%] flex flex-col", isUser ? "items-end" : "items-start")}>
        <div
          className={clsx(
            "px-4 py-2.5 rounded-bubble text-[15px] leading-relaxed whitespace-pre-wrap break-words",
            isUser
              ? "bg-sage text-cream rounded-br-sm"
              : "bg-white border border-cream-border text-soil rounded-bl-sm shadow-soft",
            streaming && "caret"
          )}
        >
          {text || (streaming ? "" : "")}
        </div>
        {!isUser && !streaming && text && (
          <AudioReplayPill text={text} language={language} />
        )}
      </div>
    </motion.div>
  );
}
