import { useLayoutEffect, useRef, useState, type ElementType } from "react";
import { type TooltipProps, ValueTooltip } from "./tooltip-value";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";


export type TimelineEvent = {
    date: Date,
    icon?: ElementType,
    tooltip?: TooltipProps
};

export function Timeline({ events, mergeThreshold=20, labels=true, className="" }: { events: TimelineEvent[], mergeThreshold?: number, labels?: boolean, className?: string }) {
    // tooltip on icons
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

    const reservedPx = 50;
    const clamp = (pos: number) => {
        if (!width || width <= 0) return pos;
        const x = (pos / 100) * width;
        const clamped = Math.min(Math.max(x, reservedPx), Math.max(width - reservedPx, reservedPx));
        return (clamped / width) * 100;
    }
    const firstPos = clamp(mergedGroups[0].pos);
    const lastPos = clamp(mergedGroups[mergedGroups.length - 1].pos);
    const iconHeight = 1.3;
    const iconPadding = 1;
    const lineHeight = 0.2;
    const markerRadius = 0.5;
    const labelPadding = 0.2;
    const labelHeight = 0.9;
    const hasIcons = !events.every(evt => evt.icon == undefined);
    const height = (hasIcons ? iconHeight + iconPadding : 0) + markerRadius + (labels ? labelHeight + labelPadding : 0);

    return (
        <div className={`w-full ${className}`} aria-hidden>
            <div ref={containerRef} className="relative w-full" style={{ boxSizing: "border-box", height: `${height}rem` }}>

                {/* Icons */}
                {hasIcons && mergedGroups.map((group, idx) => {
                    const pos = clamp(group.pos);
                    return (
                        <div key={idx} className="absolute flex flex-col items-center top-0" style={{ left: `${pos}%`, transform: "translateX(-50%)" }}>
                            <div className="flex gap-1 items-center justifiy-center">
                                {group.events.map((evt, j) => {
                                    if (!evt.icon) return null;
                                    return (
                                        <div key={j} className="text-gray-700" style={{ lineHeight: 1, height: `${iconHeight}rem`, width: `${iconHeight}rem` }}>
                                            <TooltipProvider>
                                                <Tooltip disableHoverableContent>
                                                    <TooltipTrigger asChild>
                                                        {evt.icon && <evt.icon className="h-full w-full" />}
                                                    </TooltipTrigger>
                                                    {evt.tooltip && (<TooltipContent className="max-w-xs text-sm p-3 pointer-events-none" side="bottom">
                                                        <ValueTooltip label={evt.tooltip.label} description={evt.tooltip.description} alternatives={evt.tooltip.alternatives} />
                                                    </TooltipContent>)}
                                                </Tooltip>
                                            </TooltipProvider>
                                        </div>
                                    )
                                })}
                            </div>
                        </div>
                    )
                })}

                {/* Timeline line */}
                <div className="absolute pointer-events-none" style={{ left: `${firstPos}%`, right: `${100 - lastPos}%`, transform: "translateY(-50%)", top: `${hasIcons ? iconHeight + iconPadding : 0}rem` }}>
                    <div className="bg-gray-300 rounded w-full" style={{ height: `${lineHeight}rem` }} />
                </div>

                {/* Markers */}
                {mergedGroups.map((group, idx) => {
                    const pos = clamp(group.pos);
                    return (
                        <div key={idx} className={`absolute flex flex-col items-center`} style={{ left: `${pos}%`, transform: "translateX(-50%) translateY(-50%)", top: `${hasIcons ? iconHeight + iconPadding : 0}rem`, width: `${markerRadius * 2}rem`, height: `${markerRadius * 2}rem` }}>
                            <div className="w-full h-full bg-blue-500 rounded-full border-2 border-white shadow" />
                        </div>
                    )
                })}

                {/* Labels */}
                {labels && mergedGroups.map((group, idx) => {
                    const pos = clamp(group.pos);
                    return (
                        <div key={idx} className="absolute flex flex-col items-center bottom-0" style={{ left: `${pos}%`, transform: "translateX(-50%)", height: `${labelHeight + labelPadding}rem`, paddingTop: `${labelPadding}rem` }}>
                            <div className="text-sm font-normal text-gray-700 whitespace-nowrap items-center h-full justify-center align-bottom">
                                {[... new Set(group.events.map((evt) => ("'" + evt.date.getFullYear().toString().substring(2))))].join(" | ")}
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    );
}