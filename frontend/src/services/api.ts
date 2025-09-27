export const API_BASE = "http://localhost:8000/api/v1";

export async function getLatestBatch(bounds?: {
    lat_min: number;
    lat_max: number;
    lon_min: number;
    lon_max: number;
}) {
    const params = bounds ? `?lat_min=${bounds.lat_min}&lat_max=${bounds.lat_max}&lon_min=${bounds.lon_min}&lon_max=${bounds.lon_max}` : "";
    const res = await fetch(`${API_BASE}/maps${params}`);
    if (!res.ok) throw new Error("Failed to fetch latest batch");
    return res.json();
}


export async function getAircraftTrack(icao24: string) {
    const res = await fetch(`${API_BASE}/maps/track/${icao24}`);
    if (!res.ok) throw new Error("Failed to fetch aircraft track");
    return res.json();
}

export async function getAircraftDetails(icao24: string) {
    const res = await fetch(`${API_BASE}/aircraft/${icao24}`);
    if (!res.ok) throw new Error("Failed to fetch aircraft details");
    return res.json();
}

export async function getAircraftImages(icao24: string) {
    const res = await fetch(`${API_BASE}/aircraft/${icao24}/photos`);
    if (!res.ok) throw new Error("Failed to fetch aircraft details");
    return res.json();
}
