"use client";

import { AnimatePresence, motion, useMotionValueEvent, useScroll } from "motion/react";
import { useRef, useState } from "react";

export type StoryStep = {
  id: string;
  eyebrow: string;
  title: string;
  body: React.ReactNode;
  visual: React.ReactNode;
};

/**
 * One pinned stage for several feature sections. The copy and the visual swap
 * as the page scrolls past; below `lg` the steps simply stack.
 */
export function Story({ steps }: { steps: StoryStep[] }) {
  const ref = useRef<HTMLElement>(null);
  const [step, setStep] = useState(0);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start start", "end end"] });
  useMotionValueEvent(scrollYProgress, "change", (v) => {
    setStep(Math.min(steps.length - 1, Math.max(0, Math.floor(v * steps.length))));
  });
  const current = steps[step];

  return (
    <>
      <section
        ref={ref}
        id="read"
        className="relative hidden border-t border-rule/70 lg:block"
        style={{ height: `${steps.length * 100}vh` }}
      >
        <div className="sticky top-0 flex h-screen items-center overflow-hidden">
          <div className="mx-auto grid w-full max-w-[76rem] grid-cols-12 items-center gap-10 px-12">
            <div className="col-span-4">
              <ol className="mb-10 flex flex-col gap-2.5">
                {steps.map((s, i) => (
                  <li key={s.id} className="flex items-center gap-3">
                    <span className="relative h-px w-10 overflow-hidden bg-rule">
                      <motion.span
                        className="absolute inset-0 origin-left bg-ink"
                        animate={{ scaleX: i <= step ? 1 : 0 }}
                        transition={{ duration: 0.5 }}
                      />
                    </span>
                    <span
                      className={`text-[13px] transition-colors duration-300 ${
                        i === step ? "text-ink" : "text-ink/40"
                      }`}
                    >
                      {s.eyebrow}
                    </span>
                  </li>
                ))}
              </ol>
              <AnimatePresence mode="wait">
                <motion.div
                  key={current.id}
                  initial={{ opacity: 0, y: 18 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -12 }}
                  transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
                >
                  <h2 className="t-heading text-[2.1rem] text-ink">{current.title}</h2>
                  <div className="mt-5 text-[1rem] leading-[1.65] text-ink/70">{current.body}</div>
                </motion.div>
              </AnimatePresence>
            </div>
            <div className="relative col-span-8 flex min-h-[36rem] items-center justify-center">
              <AnimatePresence mode="wait">
                <motion.div
                  key={current.id}
                  className="w-full"
                  initial={{ opacity: 0, scale: 0.97, filter: "blur(6px)" }}
                  animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
                  exit={{ opacity: 0, scale: 1.02, filter: "blur(6px)" }}
                  transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
                >
                  {current.visual}
                </motion.div>
              </AnimatePresence>
            </div>
          </div>
        </div>
      </section>

      <div className="lg:hidden">
        {steps.map((s) => (
          <section key={s.id} className="border-t border-rule/70 px-5 py-16 sm:px-8">
            <p className="t-eyebrow">{s.eyebrow}</p>
            <h2 className="t-heading mt-4 text-[1.9rem] text-ink">{s.title}</h2>
            <div className="mt-5 text-[1rem] leading-[1.65] text-ink/70">{s.body}</div>
            <div className="mt-10">{s.visual}</div>
          </section>
        ))}
      </div>
    </>
  );
}
