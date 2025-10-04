import { type Airline } from "@/types/api";
import { apiClient } from "./client";


export interface AirlineSearchParams {
    icao?: string;
    iata?: string;
    name?: string;
    callsign?: string;
    types?: (
        | "SCHEDULED"
        | "CHARTER"
        | "CARGO"
        | "VIRTUAL"
        | "LEISURE"
        | "GOVERNMENT"
        | "PRIVATE"
        | "MANUFACTURER"
        | "SUPPLIER"
        | "DIVISION"
    )[];
    country?: string;
    hub?: string;
    limit?: number;
}


export async function searchAirline(params: AirlineSearchParams = {}): Promise<Airline[]> {
    const { data } = await apiClient.get<Airline[]>("/airline", { params });
    return data;
}

export async function getAirline(icao: string): Promise<Airline> {
    const { data } = await apiClient.get<Airline>(`/airline/${icao}`)
    return data;
}
