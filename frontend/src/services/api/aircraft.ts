import { type Aircraft, type AircraftPhoto } from "@/types/api";
import { apiClient } from "./client";


export interface AircraftSearchParams {
    registration?: string;
    icao24?: string;
    callsign?: string;
    model?: string;
    airline?: string;
    engine_count?: 2 | 3 | 4;
    engine_type?: "JET" | "TURBOPROP" | "TURBOFAN" | "UNKNOWN";
    limit?: number;
}

export interface AircraftPhotosParams {
    limit?: number
}


export async function searchAircraft(params: AircraftSearchParams = {}): Promise<Aircraft[]> {
    const { data } = await apiClient.get<Aircraft[]>("/aircraft", { params });
    return data;
}

export async function getAircraft(registration: string): Promise<Aircraft> {
    const { data } = await apiClient.get<Aircraft>(`/aircraft/${registration}`);
    return data;
}

export async function getAircraftPhotos(registration: string, params: AircraftPhotosParams = {}): Promise<AircraftPhoto[]> {
    const { data } = await apiClient.get<AircraftPhoto[]>(`/aircraft/${registration}/photos`, { params });
    return data;
}
