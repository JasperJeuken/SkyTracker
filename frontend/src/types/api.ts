export type AircraftDetails = {
    time: string
    data_source: number,
    aircraft_iata: string,
    aircraft_icao: string,
    aircraft_icao24: string,
    aircraft_registration: string,
    airline_iata: string,
    airline_icao: string,
    arrival_iata: string,
    arrival_icao: string,
    departure_iata: string,
    departure_icao: string,
    flight_iata: string,
    flight_icao: string,
    flight_number: string,
    position: [number, number],
    geo_altitude: number | null,
    baro_altitude: number | null,
    heading: number | null,
    speed_horizontal: number | null,
    speed_vertical: number | null,
    is_on_ground: boolean,
    status: number,  // TODO make string
    squawk: number | null,
    squawk_time: string | null,
    aircraft_country: string,
};

export type AircraftImage = {
    image_url: string,
    detail_url: string,
};

export type AircraftSimpleState = {
    callsign: string,
    position: [number, number],
    heading: number | null,
}

export type AircraftDetailedState = {
    time: string,
    callsign: string,
    position: [number, number],
    heading: number | null,
    altitude: number | null,
}
