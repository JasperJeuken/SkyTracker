import { useEffect, useState } from "react";
import { Polyline } from "react-leaflet";
import { type AircraftState } from "./AircraftMapProvider"
import { getAircraftTrack } from "../services/api";


function altitudeToColor(altitude: number | null): string {
    if (altitude == null) return "#888";
    const maxAlt = 12000;
    const ratio = Math.min(1, Math.max(0, altitude / maxAlt))
    const r = Math.round(255 * ratio);
    const b = Math.round(255 * (1 - ratio));
    return `rgb(${r},0,${b})`
}


export function AircraftTrackLayer({ icao24, pane }: { icao24: string | null, pane: string }) {
    const [track, setTrack] = useState<AircraftState[]>([]);

    // Update track if selected aircraft changes
    useEffect(() => {
        if (!icao24) {
            setTrack([]);
            return;
        }
        getAircraftTrack(icao24)
            .then(setTrack)
            .catch(() => setTrack([]));
    }, [icao24]);
    if (!track || track.length < 2) return null;

    // Parse line segments from state history
    const segments: {
        positions: [number, number][];
        type: "gap" | "normal";
        startAlt: number | null;
        endAlt: number | null;
    }[] = []
    for (let i = 0; i < track.length - 1; i++) {
        const p1 = track[i];
        const p2 = track[i + 1];
        const dt = p1.time - p2.time;

        if (dt > 180) {
            segments.push({
                positions: [[p1.latitude, p1.longitude], [p2.latitude, p2.longitude]],
                type: "gap",
                startAlt: null,
                endAlt: null,
            });
        } else {
            segments.push({
                positions: [[p1.latitude, p1.longitude], [p2.latitude, p2.longitude]],
                type: "normal",
                startAlt: p1.altitude,
                endAlt: p2.altitude
            });
        }
    }

    // Create polyline segments
    return (
        <>
            {segments.map((seg, idx) => (
                seg.type === "gap" ? (
                    <Polyline key={idx} positions={seg.positions} pathOptions={{ color: "grey", weight: 2, dashArray: "6, 8" }} pane={pane}/>
                ) : (
                    <Polyline key={idx} positions={seg.positions} pathOptions={{ color: altitudeToColor(seg.endAlt), weight: 3 }} pane={pane} />
                )
            ))}
        </>
    );
}
