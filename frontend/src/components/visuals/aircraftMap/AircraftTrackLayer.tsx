import { useEffect, useMemo, useState } from "react";
import { Polyline } from "react-leaflet";
import { type DetailedMapState } from "@/types/api";
import { getHistoryStates } from "@/services/api/state";


function altitudeToColor(altitude: number | null): string {
    if (altitude == null) return "#888";
    const maxAlt = 12000;
    const ratio = Math.min(1, Math.max(0, altitude / maxAlt))
    const r = Math.round(255 * ratio);
    const b = Math.round(255 * (1 - ratio));
    return `rgb(${r},0,${b})`
}


export function AircraftTrackLayer({ callsign, pane }: { callsign: string | null, pane: string }) {
    const [track, setTrack] = useState<DetailedMapState[]>([]);
    const [visibleSegments, setVisibleSegments] = useState<number>(0);

    // Update track if selected aircraft changes
    useEffect(() => {
        if (!callsign) {
            setTrack([]);
            setVisibleSegments(0);
            return;
        }
        getHistoryStates(callsign)
            .then(track =>{
                setTrack(track);
                setVisibleSegments(0);
            })
            .catch(() => setTrack([]));
    }, [callsign]);
    // if (!track || track.length < 2) return null;

    // Parse line segments from state history
    const segments = useMemo(() => {
        if (!track || track.length < 2) return [];
        const segs: {
            positions: [number, number][];
            type: "gap" | "normal";
            startAlt: number | null;
            endAlt: number | null;
        }[] = []
        for (let i = 0; i < track.length - 1; i++) {
            const p1 = track[i];
            const p2 = track[i + 1];
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
    }, [track]);
    

    // Animate segment reveal
    useEffect(() => {
        if (segments.length === 0) {
            setVisibleSegments(0);
            return;
        }
        setVisibleSegments(0);
        let i = 0;
        const interval = setInterval(() => {
            i++;
            setVisibleSegments(i);
            if (i >= segments.length) clearInterval(interval);
        }, 10);
        return () => clearInterval(interval);
    }, [segments]);

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
