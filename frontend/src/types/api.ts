export type State = {
    time: string,
    data_source: string,
    status: string,
    aircraft: {
        iata: string | null,
        icao: string | null,
        icao24: string | null,
        registration: string | null,
    },
    airline: {
        iata: string | null,
        icao: string | null,
    },
    airport: {
        arrival_iata: string | null,
        arrival_icao: string | null,
        departure_iata: string | null,
        departure_icao: string | null,
    },
    flight: {
        iata: string | null,
        icao: string,
        number: number | null,
    },
    geography: {
        position: [number, number],
        geo_altitude: number | null,
        baro_altitude: number | null,
        heading: number | null,
        speed_horizontal: number | null,
        speed_vertical: number | null,
        is_on_ground: boolean,
    },
    transponder: {
        squawk: number | null,
        squawk_time: string | null,
    },
}

export type SimpleMapState = {
    callsign: string,
    position: [number, number],
    heading: number | null,
    model: string | null,
}

export type DetailedMapState = {
    time: string,
    callsign: string,
    position: [number, number],
    heading: number | null,
    altitude: number | null,
}

export type Airline = {
    iata: string | null,
    icao: string | null,
    name: string | null,
    callsign: string | null,
    founding: number | null,
    fleet_age: number | null,
    fleet_size: number | null,
    status: string,
    types: string[],
    country_iso2: string | null,
    hub_iata: string | null,
}

export type Airport = {
    iata: string,
    icao: string | null,
    name: string,
    latitude: number | null,
    longitude: number | null,
    geoname_id: number | null,
    phone: string | null,
    timezone: string | null,
    gmt: string | null,
    city_iata: string | null,
    country_iso2: string,
    country_name: string,
}

export type Aircraft = {
    identity: {
        icao24: string | null,
        registration: string | null,
        test_registration: string | null,
        owner: string | null,
        airline_iata: string | null,
        airline_icao: string | null,
    },
    model: {
        type_iata: string | null,
        type_iata_code_short: string | null,
        type_iata_code_long: string | null,
        engine_count: number | null,
        engine_type: string | null,
        model_code: string | null,
        line_number: string | null,
        serial_number: string | null,
        family: string | null,
        sub_family: string | null,
        series: string | null,
        classification: string,
    },
    lifecycle: {
        date_delivery: string | null,
        date_first_flight: string | null,
        date_registration: string | null,
        date_rollout: string | null,
        age: number | null,
    },
    status: string,
}

export type AircraftPhoto = {
    image_url: string,
    detail_url: string,
}
