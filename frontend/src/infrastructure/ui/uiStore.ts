import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UIStore {
  isSidebarCollapsed: boolean;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  dismissedModals: Set<string>;
  dismissModal: (modalId: string) => void;
  isDismissed: (modalId: string) => boolean;
  resetDismissed: () => void;
}

export const useUIStore = create<UIStore>()(
  persist(
    (set, get) => ({
      isSidebarCollapsed: false,
      toggleSidebar: () =>
        set((state) => ({ isSidebarCollapsed: !state.isSidebarCollapsed })),
      setSidebarCollapsed: (collapsed) =>
        set({ isSidebarCollapsed: collapsed }),
      dismissedModals: new Set<string>(),
      dismissModal: (modalId: string) =>
        set((state) => {
          const newSet = new Set(state.dismissedModals);
          newSet.add(modalId);
          return { dismissedModals: newSet };
        }),
      isDismissed: (modalId: string) => get().dismissedModals.has(modalId),
      resetDismissed: () => set({ dismissedModals: new Set<string>() }),
    }),
    {
      name: 'freelansign-ui-storage',
      partialize: (state) => ({
        isSidebarCollapsed: state.isSidebarCollapsed,
        dismissedModals: Array.from(state.dismissedModals),
      }),
      merge: (persistedState, currentState) => ({
        ...currentState,
        ...(persistedState as object),
        dismissedModals: new Set(
          (persistedState as { dismissedModals?: string[] })?.dismissedModals ||
            [],
        ),
      }),
    },
  ),
);
