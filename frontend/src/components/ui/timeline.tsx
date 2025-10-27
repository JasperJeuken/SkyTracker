import { useLayoutEffect, useRef, useState, type ReactNode } from "react";
import { Calendar } from "lucide-react";


type TimelineEvent = {
    date: Date,
    icon?: ReactNode
};

export function Timeline({ events, mergeThreshold=5 }: { events: TimelineEvent[], mergeThreshold?: number }) {
    if (!events || events.length === 0) return null;
    const containerRef = useRef<HTMLDivElement | null>(null);
    const [width, setWidth] = useState<number>(0);

    // Responsive width
    useLayoutEffect(() => {
        const elem = containerRef.current;
        if (!elem) return;
        const ro = new (window as any).ResizeObserver(() => {
            setWidth(elem.clientWidth || 0);
        })
        ro.observe(elem);
        setWidth(elem.clientWidth || 0);
        return () => ro.disconnect();
    }, []);

    // Calculate start, end, span
    const sortedDates = [...events].sort((a, b) => a.date.getTime() - b.date.getTime());
    const minDate = sortedDates[0].date.getTime();
    const maxDate = sortedDates[sortedDates.length - 1].date.getTime();
    const span = Math.max(1, maxDate - minDate);

    // Calculate normalized positions (merge close dates)
    const rawPositions = sortedDates.map((e) => (
        (e.date.getTime() - minDate) / span * 100
    ));
    const mergedGroups: { pos: number; events: TimelineEvent[] }[] = [];
    sortedDates.forEach((event, i) => {
        const rawPos = rawPositions[i];
        const prev = mergedGroups[mergedGroups.length - 1];
        if (prev && Math.abs(prev.pos - rawPos) < mergeThreshold) {
            prev.events.push(event);
            prev.pos = (prev.pos * (prev.events.length - 1) + rawPos) / prev.events.length;
        } else {
            mergedGroups.push({ pos: rawPos, events: [event] });
        }
    });

    const markerDiameter = 16;
    const iconMaxWidth = 20;
    const verticalPadding = 8;
    const reservedPx = Math.ceil(markerDiameter / 2 + iconMaxWidth / 2 + verticalPadding);

    const clamp = (pos: number) => {
        if (!width || width <= 0) return pos;
        const x = (pos / 100) * width;
        const clamped = Math.min(Math.max(x, reservedPx), Math.max(width - reservedPx, reservedPx));
        return (clamped / width) * 100;
    }
    const firstPos = clamp(mergedGroups[0].pos);
    const lastPos = clamp(mergedGroups[mergedGroups.length - 1].pos);

    return (
        <div className="w-full" aria-hidden>
            <div ref={containerRef} className="relative w-full py-6" style={{ boxSizing: "border-box" }}>

                {/* Timeline line */}
                <div className="absolute top-1/2 -translate-y-1/2 pointer-events-none" style={{ left: `${firstPos}%`, right: `${100 - lastPos}%` }}>
                    <div className="h-1 bg-gray-300 rounded w-full" />
                </div>

                {/* Markers */}
                {mergedGroups.map((group, idx) => {
                    const pos = clamp(group.pos);
                    return (
                        <div key={idx} className="absolute flex flex-col items-center" style={{ left: `${pos}%`, transform: "translateX(-50%) translateY(-50%)", top: "50%" }}>
                            {/* Icons */}
                            <div className="flex gap-1 mb-2 items-center justify-center">
                                {group.events.map((evt, j) => (
                                    <div key={j} className="text-gray-700" style={{ lineHeight: 1 }}>
                                        {evt.icon || <Calendar size={16} />}
                                    </div>
                                ))}
                            </div>

                            {/* Circle marker */}
                            <div className="w-4 h-4 bg-blue-500 rounded-full border-2 border-white shadow" />

                            {/* Date labels */}
                            <div className="text-xs mt-2 text-gray-600 whitespace-nowrap">
                                {group.events.map((evt) => evt.date.toLocaleDateString()).join(" | ")}
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    );
}