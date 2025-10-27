import { useRef, type ReactNode } from "react";
import { Calendar } from "lucide-react";


type TimelineEvent = {
    date: Date,
    icon?: ReactNode
};

export function Timeline({ events, mergeThreshold=5 }: { events: TimelineEvent[], mergeThreshold?: number }) {
    if (!events || events.length === 0) return null;

    // Calculate start, end, span
    const sortedDates = [...events].sort((a, b) => a.date.getTime() - b.date.getTime());
    const minDate = sortedDates[0].date.getTime();
    const maxDate = sortedDates[sortedDates.length - 1].date.getTime();
    const span = maxDate - minDate || 1;

    // Calculate normalized positions (merge close dates)
    const positions = sortedDates.map((e) => (
        (e.date.getTime() - minDate) / span * 100
    ));
    const mergedGroups: { pos: number; events: TimelineEvent[] }[] = [];
    sortedDates.forEach((event, i) => {
        const pos = positions[i];
        const prev = mergedGroups[mergedGroups.length - 1];
        if (prev && Math.abs(prev.pos - pos) < mergeThreshold) {
            prev.events.push(event);
        } else {
            mergedGroups.push({ pos, events: [event] });
        }
    });

    return (
        <div className="relative w-full h-32">
            <div className="absolute top-1/2 left-0 w-full h-1 bg-gray-300 rounded" />

            {mergedGroups.map((group, i) => (
                <div key={i} className="absolute flex flex-col items-center" style={{ left: `${group.pos}%`, transform: "translateX(-50%)" }}>
                    <div className="flex gap-1 mb-2">
                        {group.events.map((ev, j) => (
                            <div key={j} className="text-gray-700">
                                {ev.icon || <Calendar size={16} />}
                            </div>
                        ))}
                    </div>
                    <div className="w-4 h-4 bg-blue-500 rounded-full border-2 border-white shadow" />
                    <div className="text-xs mt-1 text-gray-600 whitespace-nowrap">
                        {group.events.map((ev) => ev.date.toLocaleDateString()).join(" | ")}
                    </div>
                </div>
            ))}
        </div>
    );
}