import { useMapStore } from "@/store/mapStore";
import { useEffect, useRef, useState } from "react";
import { Polyline } from "react-leaflet";


function altitudeToColor(altitude: number | null): string {
    if (altitude == null) return "#888";
    const maxAlt = 12000;
    const ratio = Math.min(1, Math.max(0, altitude / maxAlt))
    const r = Math.round(255 * ratio);
    const b = Math.round(255 * (1 - ratio));
    return `rgb(${r},0,${b})`
}


type TrackSegment = {
    startPos: [number, number],
    endPos: [number, number],
    startAlt: number | null,
    endAlt: number | null,
    startTime: string,
    endTime: string,
    type: "normal" | "gap" | "current",
};


function createPolyline(segment: TrackSegment, pane: string) {
    const key = Math.random().toString(16).slice(2);
    if (segment.type === "gap") {
        return <Polyline key={key} positions={[segment.startPos, segment.endPos]} pathOptions={{ color: "grey", weight: 2, dashArray: "6, 8" }} pane={pane} />;
    } else if (segment.type === "normal") {
        return <Polyline key={key} positions={[segment.startPos, segment.endPos]} pathOptions={{ color: altitudeToColor(segment.endAlt), weight: 3 }} pane={pane} />;
    } 
    return <Polyline key={key} positions={[segment.startPos, segment.endPos]} pathOptions={{ color: altitudeToColor(segment.endAlt), weight: 3, dashArray: "6, 8" }} pane={pane} />;
}


export function AircraftTrackLayer({ pane }: { pane: string }) {
    // Store data
    const history = useMapStore((state) => state.history)
    const animatedPosition = useMapStore((state) => state.animatedPosition);
    const selected = useMapStore((state) => state.selected);
    const mapRef = useMapStore((state) => state.mapRef);
    const animationZoomLimit = useMapStore((state) => state.animationZoomLimit);

    // Rendering
    const [segments, setSegments] = useState<TrackSegment[]>([]);
    const [visibleSegments, setVisibleSegments] = useState<TrackSegment[]>([]);
    const [currentSegment, setCurrentSegment] = useState<TrackSegment | null>(null);
    const prevTrackLength = useRef<number>(0);
    const prevSelected = useRef<string | null>(null);

    // Update segments
    useEffect(() => {
        const newSegments: TrackSegment[] = [];
        for (let i = 0; i < history.length - 1; i++) {
            const state1 = history[i];
            const state2 = history[i + 1];
            
            const dt = (new Date(state1.time).valueOf() - new Date(state2.time).valueOf()) / 1000;
            const type = dt < 200 ? "normal" : "gap";
            newSegments.push({
                startPos: state2.position,
                endPos: state1.position,
                startAlt: state2.altitude,
                endAlt: state1.altitude,
                startTime: state2.time,
                endTime: state1.time,
                type,
            });
        }
        setSegments(newSegments)
    }, [history]);

    // Animate segment reveal
    useEffect(() => {
        if (!selected || segments.length == 0) {
            setVisibleSegments([]);
            prevSelected.current = null;
            prevTrackLength.current = 0;
            return;
        }
        let isCancelled = false;
        
        const addSegments = (count: number) => {
            let i = 0;
            const interval = setInterval(() => {
                if (isCancelled) {
                    clearInterval(interval);
                    return;
                }
                const segment = segments[i];
                if (!segment) return;
                setVisibleSegments((prev) => [...prev, segment]);
                i++;
                if (i >= count) clearInterval(interval);
            }, 10);
        };

        const diff = segments.length - prevTrackLength.current;
        if (selected != prevSelected.current || diff > 1) {
            setVisibleSegments([]);
            addSegments(segments.length);
        } else {
            if (diff > 0) addSegments(diff);
        }

        prevTrackLength.current = segments.length;
        prevSelected.current = selected;

        return () => {
            isCancelled = true;
        }
    }, [segments, selected]);

    // Animate last segment to current position
    useEffect(() => {
        if (!mapRef || !selected || segments.length == 0) {
            setCurrentSegment(null);
            return;
        }
        if (mapRef.getZoom() < animationZoomLimit) {
            setCurrentSegment(null);
            return;
        }
        
        const lastState = segments[0];
        const currentSegment: TrackSegment = {
            startPos: lastState.endPos,
            endPos: animatedPosition,
            startAlt: lastState.endAlt,
            endAlt: lastState.endAlt,
            startTime: lastState.endTime,
            endTime: new Date().toISOString(),
            type: "current",
        }
        setCurrentSegment(currentSegment);
    }, [animatedPosition, segments, selected, mapRef]);

    return (
        <>
            {visibleSegments.map((seg) => createPolyline(seg, pane))}
            {currentSegment && createPolyline(currentSegment, pane)}
        </>
    );
}
