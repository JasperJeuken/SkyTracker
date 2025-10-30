const g0 = 9.80665;
const R = 287.05;
const gamma = 1.4;


type AtmosphereLayer = {
    lapseRate: number;
    heightBase: number,
    temperatureBase: number;
    pressureBase: number;
    densityBase: number;
};

const layers: AtmosphereLayer[] = [
    { lapseRate: -0.0065, heightBase: 0, temperatureBase: 288.15, pressureBase: 101325, densityBase: 1.225 },
    { lapseRate: 0.0, heightBase: 11000, temperatureBase: 216.65, pressureBase: 22632, densityBase: 0.3639 },
    { lapseRate: 0.001, heightBase: 20000, temperatureBase: 216.65, pressureBase: 5474.9, densityBase: 0.0880 },
    { lapseRate: 0.0028, heightBase: 32000, temperatureBase: 228.65, pressureBase: 868.02, densityBase: 0.0132 },
    { lapseRate: 0.0, heightBase: 47000, temperatureBase: 270.65, pressureBase: 110.91, densityBase: 0.0014 },
    { lapseRate: -0.0028, heightBase: 51000, temperatureBase: 270.65, pressureBase: 66.939, densityBase: 0.0009 },
    { lapseRate: -0.002, heightBase: 71000, temperatureBase: 214.65, pressureBase: 3.9564, densityBase: 0.0001 },
];

function getAtmosphericProperties(altitude: number): { temperature: number, pressure: number, density: number } {
    const h = Math.min(Math.max(altitude, 0), 85000);

    // Find layer
    let layerIdx = 0;
    for (let i = layers.length - 1; i >= 0; i--) {
        if (h >= layers[i].heightBase) {
            layerIdx = i;
            break;
        }
    }
    const { lapseRate, heightBase, temperatureBase, pressureBase } = layers[layerIdx];
    const dh = h - heightBase;

    // Calculate temperature, pressure, density
    const temperature = temperatureBase + lapseRate * dh;
    let pressure: number;
    if (Math.abs(lapseRate) > 1e-6) {
        pressure = pressureBase * Math.pow(temperatureBase / temperature, (g0 / (R * lapseRate)));
    } else {
        pressure = pressureBase * Math.exp(-g0 * dh / (R * temperatureBase));
    }
    const density = pressure / (R * temperature);

    return { temperature, pressure, density };
}

function getSpeedOfSound(altitude: number): number {
    const { temperature } = getAtmosphericProperties(altitude);
    return Math.sqrt(gamma * R * temperature);
}


export function getMachNumber(altitude: number, velocity: number): number {
    const a = getSpeedOfSound(altitude);
    return velocity / a;
}
