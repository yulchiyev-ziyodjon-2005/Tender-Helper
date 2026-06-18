import { Link } from 'react-router-dom';

export default function BrandMark({ compact = false, to = '/', inverse = false }) {
  return (
    <Link
      to={to}
      className="inline-flex items-center gap-3 rounded-xl focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400"
      aria-label="Tender-Helper AI bosh sahifasi"
    >
      <span className="relative grid h-10 w-10 place-items-center overflow-hidden rounded-xl bg-gradient-to-br from-blue-600 via-indigo-600 to-cyan-500 shadow-lg shadow-blue-500/20">
        <svg viewBox="0 0 40 40" className="h-7 w-7" aria-hidden="true">
          <path d="M8 10h24M20 10v21M12 18h16M15 31h10" fill="none" stroke="white" strokeWidth="3" strokeLinecap="round" />
          <circle cx="20" cy="10" r="3" fill="white" />
        </svg>
      </span>
      {!compact && (
        <span className={`leading-none ${inverse ? 'text-white' : 'text-slate-950 dark:text-white'}`}>
          <span className="block text-[15px] font-extrabold tracking-tight">Tender-Helper</span>
          <span className="mt-1 block text-[10px] font-bold uppercase tracking-[0.24em] text-cyan-500">AI Platform</span>
        </span>
      )}
    </Link>
  );
}
