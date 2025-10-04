import { type State, type SimpleMapState, type DetailedMapState } from "@/types/api";
import { apiClient } from "./client";


export interface StateSearchParams {
    callsign?: string;
    status?: "UNKNOWN" | "STARTED" | "LANDED" | "EN_ROUTE";
    model?: string;
    registration?: string;
    airline?: string;
    arrival?: string;
    departure?: string;
    on_ground?: boolean;
    squawk?: string;
    limit?: number;
}

export interface StateNearbyParams {
    radius?: number;
    limit?: number;
}

export interface StateAreaParams {
    south?: number;
    north?: number;
    west?: number;
    east?: number;
    limit?: number;
}

export interface StateHistoryParams {
    duration?: string;
    limit?: number;
}

export async function searchState(params: StateSearchParams = {}): Promise<State[]> {
    const { data } = await apiClient.get<State[]>("/state", { params });
    return data;
}

export async function getNearbyStates(lat: number, lon: number, params: StateNearbyParams): Promise<SimpleMapState[]> {
    const { data } = await apiClient.get<SimpleMapState[]>(`/state/nearby?lat=${lat}&lon=${lon}`, { params });
    return data
}

export async function getAreaStates(params: StateAreaParams = {}): Promise<SimpleMapState[]> {
    const { data } = await apiClient.get<SimpleMapState[]>("/state/area", { params });
    return data
}

export async function getLatestState(callsign: string): Promise<State> {
    const { data } = await apiClient.get<State>(`/state/${callsign}/latest`);
    return data;
}

export async function getHistoryStates(callsign: string, params: StateHistoryParams = {}): Promise<DetailedMapState[]> {
    const { data } = await apiClient.get<DetailedMapState[]>(`/state/${callsign}/history`, { params });
    return data;
}
