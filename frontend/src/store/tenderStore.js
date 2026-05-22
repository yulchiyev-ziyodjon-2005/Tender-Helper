/**
 * TenderHelper AI — Tender Store (Zustand)
 * ==========================================
 * Tender lotlari va filtrlarni boshqarish.
 */

import { create } from 'zustand';

const useTenderStore = create((set) => ({
  // Tenderlar ro'yxati
  tenders: [],
  setTenders: (tenders) => set({ tenders }),

  // Tanlangan tender
  selectedTender: null,
  setSelectedTender: (tender) => set({ selectedTender: tender }),

  // Qidiruv
  searchQuery: '',
  setSearchQuery: (query) => set({ searchQuery: query }),

  // Filtrlar
  filters: {
    region: '',
    category: '',
    platform_source: '',
    status: 'active',
    min_price: '',
    max_price: '',
  },
  setFilter: (key, value) =>
    set((state) => ({
      filters: { ...state.filters, [key]: value },
    })),
  resetFilters: () =>
    set({
      filters: {
        region: '',
        category: '',
        platform_source: '',
        status: 'active',
        min_price: '',
        max_price: '',
      },
    }),

  // Pagination
  currentPage: 1,
  totalPages: 1,
  setCurrentPage: (page) => set({ currentPage: page }),
  setTotalPages: (total) => set({ totalPages: total }),

  // Loading
  isLoading: false,
  setLoading: (isLoading) => set({ isLoading }),
}));

export default useTenderStore;
