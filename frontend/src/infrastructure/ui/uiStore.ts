import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UIStore {
  isSidebarCollapsed: boolean;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
}

export const useUIStore = create<UIStore>()(
  persist(
    (set) => ({
      isSidebarCollapsed: false,
      toggleSidebar: () =>
        set((state) => ({ isSidebarCollapsed: !state.isSidebarCollapsed })),
      setSidebarCollapsed: (collapsed) =>
        set({ isSidebarCollapsed: collapsed }),
    }),
    {
      name: 'freelansign-ui-storage',
    },
  ),
);
