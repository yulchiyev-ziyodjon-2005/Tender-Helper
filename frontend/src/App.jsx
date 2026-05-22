/**
 * TenderHelper AI — Root App Component
 * =======================================
 * QueryClient provider va router o'rnatilgan.
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEffect } from 'react';
import AppRouter from './routes/AppRouter';
import useUIStore from './store/uiStore';

// React Query konfiguratsiyasi
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,    // 5 daqiqa — ma'lumot yangi hisoblanadi
      retry: 1,                     // 1 marta qayta urinish
      refetchOnWindowFocus: false,  // Tab o'tganda qayta yuklamaslik
    },
  },
});

export default function App() {
  const isDarkMode = useUIStore((state) => state.isDarkMode);

  // Dark mode klasini HTML ga qo'shish
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  return (
    <QueryClientProvider client={queryClient}>
      <AppRouter />
    </QueryClientProvider>
  );
}
