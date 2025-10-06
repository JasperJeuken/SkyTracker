import { create } from "zustand";


export interface AppState {
    headerHeight: number;
    setHeaderHeight: (height: number) => void;
};

export const useAppStore = create<AppState>()((set) => ({
    headerHeight: 0,
    setHeaderHeight: (height) => set(() => ({ headerHeight: height })),
}));
