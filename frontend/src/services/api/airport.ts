import { type Airport } from "@/types/api";
import { apiClient } from "./client";


export interface AirportSearchParams {
    iata?: string;
    icao?: string;
    name?: string;
    city?: string;
    country?: string;
    limit?: number;
}

export async function searchAirport(params: AirportSearchParams = {}): Promise<Airport[]> {
    const { data } = await apiClient.get<Airport[]>("/airport", { params });
    return data;
}

export async function getAirport(iata: string): Promise<Airport> {
    const { data } = await apiClient.get<Airport>(`/airport/${iata}`);
    return data;
}
