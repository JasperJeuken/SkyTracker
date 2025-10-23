import { useEffect, useMemo, useRef, useState } from "react";
import { Polyline } from "react-leaflet";
import { getHistoryStates } from "@/services/api/state";
import { useMapStore } from "@/store/mapStore";


function altitudeToColor(altitude: number | null): string {
    if (altitude == null) return "#888";
    const maxAlt = 12000;
    const ratio = Math.min(1, Math.max(0, altitude / maxAlt))
    const r = Math.round(255 * ratio);
    const b = Math.round(255 * (1 - ratio));
    return `rgb(${r},0,${b})`
}


export function AircraftTrackLayer({ callsign, pane }: { callsign: string | null, pane: string }) {
    const track = useMapStore((state) => callsign ? state.history[callsign] : null);
    const setHistory = useMapStore((state) => state.setHistory);
    const [visibleSegments, setVisibleSegments] = useState<number>(0);
    const prevCallsign = useRef<string | null>(null);
    const prevTrackLength = useRef<number>(0);

    // Update track if selected aircraft changes
    useEffect(() => {
        if (!callsign) {
            setVisibleSegments(0);
            return;
        }
        getHistoryStates(callsign)
            .then(newTrack =>{
                setHistory(callsign, newTrack)
                setVisibleSegments(0);
            })
            .catch(() => setHistory(callsign, []));
    }, [callsign, setHistory]);

    // Parse line segments from state history
    const segments = useMemo(() => {
        if (!callsign || !track || track.length < 2) return [];

        const sortedTrack = [...track].sort(
            (a, b) => new Date(b.time).getTime() - new Date(a.time).getTime()
        );

        const segs: {
            positions: [number, number][];
            type: "gap" | "normal";
            startAlt: number | null;
            endAlt: number | null;
        }[] = []
        for (let i = 0; i < sortedTrack.length - 1; i++) {
            const p1 = sortedTrack[i];
            const p2 = sortedTrack[i + 1];
            const t1 = new Date(p1.time).getTime() / 1000
            const t2 = new Date(p2.time).getTime() / 1000
            const dt = t1 - t2;

            if (dt > 180) {
                segs.push({
                    positions: [p1.position, p2.position],
                    type: "gap",
                    startAlt: null,
                    endAlt: null,
                });
            } else {
                segs.push({
                    positions: [p1.position, p2.position],
                    type: "normal",
                    startAlt: p1.altitude,
                    endAlt: p2.altitude
                });
            }
        }
        return segs;
    }, [track, callsign]);


    // Animate segment reveal
    useEffect(() => {
        if (!segments || segments.length === 0) {
            setVisibleSegments(0);
            prevTrackLength.current = 0;
            return;
        }
        
        if (callsign !== prevCallsign.current) {
            setVisibleSegments(0);
            let i = 0;
            const interval = setInterval(() => {
                i++;
                setVisibleSegments(i);
                if (i >= segments.length) clearInterval(interval);
            }, 10);
        } else if (segments.length > prevTrackLength.current) {
            setVisibleSegments(segments.length);
        } else if (segments.length === prevTrackLength.current) {
            // Do nothing
        } else {
            setVisibleSegments(segments.length);
        }

        prevTrackLength.current = segments.length;
        prevCallsign.current = callsign ?? null;
    }, [segments, callsign]);

    // Create polyline segments
    return (
        <>
            {segments.slice(0, visibleSegments).map((seg, idx) => (
                seg.type === "gap" ? (
                    <Polyline key={idx} positions={seg.positions} pathOptions={{ color: "grey", weight: 2, dashArray: "6, 8" }} pane={pane}/>
                ) : (
                    <Polyline key={idx} positions={seg.positions} pathOptions={{ color: altitudeToColor(seg.endAlt), weight: 3 }} pane={pane} />
                )
            ))}
        </>
    );
}
