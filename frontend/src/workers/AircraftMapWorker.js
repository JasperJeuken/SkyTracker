import { getAreaStates } from "@/services/api/state";

self.onmessage = async (e) => {
    const { bounds } = e.data;
    try {
        const data = await getAreaStates({
            south: bounds.south,
            north: bounds.north,
            west: bounds.west,
            east: bounds.east,
        });
        postMessage({ data });
    } catch (err) {
        postMessage({ error: err });
    }
};
