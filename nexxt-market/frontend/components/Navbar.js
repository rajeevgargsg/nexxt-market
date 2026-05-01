import Link from 'next/link'
import { useState, useEffect } from 'react'
import { Bell, Search, Plus, Zap, Menu, X, User } from 'lucide-react'
import { notifAPI } from '../lib/api'

export default function Navbar() {
  const [notifCount, setNotifCount] = useState(0)
  const [menuOpen, setMenuOpen] = useState(false)
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('nexxt_token')
    setIsLoggedIn(!!token)

    if (token) {
      notifAPI.get()
        .then(r => setNotifCount(r.data.filter(n => !n.is_read).length))
        .catch(() => {})
    }
  }, [])

  return (
    <nav className="sticky top-0 z-50 border-b border-[#2a2a2a] bg-[#080808]/95 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between gap-4">

        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 shrink-0">
          <div className="w-7 h-7 rounded-md bg-brand-500 flex items-center justify-center">
            <Zap size={15} className="text-white" fill="white" />
          </div>
          <span className="font-display text-xl tracking-wider text-gradient">NEXXT</span>
        </Link>

        {/* Search bar */}
        <div className="flex-1 max-w-lg hidden md:flex items-center gap-2 bg-[#111] border border-[#2a2a2a] rounded-lg px-3 h-9 focus-within:border-brand-500 transition-colors">
          <Search size={14} className="text-[#888] shrink-0" />
          <input
            type="text"
            placeholder="Search listings, categories, locations..."
            className="flex-1 bg-transparent text-sm text-[#f0f0f0] placeholder:text-[#555] outline-none"
          />
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 shrink-0">
          {/* Live ticker */}
          <div className="live-badge hidden sm:flex">
            <span className="urgent-dot" />
            LIVE
          </div>

          {isLoggedIn ? (
            <>
              {/* Notifications */}
              <Link href="/notifications" className="relative p-2 rounded-lg hover:bg-[#1a1a1a] transition-colors">
                <Bell size={18} className="text-[#888]" />
                {notifCount > 0 && (
                  <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 rounded-full text-[9px] font-bold flex items-center justify-center text-white">
                    {notifCount > 9 ? '9+' : notifCount}
                  </span>
                )}
              </Link>

              {/* Profile */}
              <Link href="/dashboard" className="p-2 rounded-lg hover:bg-[#1a1a1a] transition-colors">
                <User size={18} className="text-[#888]" />
              </Link>
            </>
          ) : (
            <Link href="/auth" className="text-sm font-medium text-[#888] hover:text-white transition-colors px-3 py-1.5">
              Sign in
            </Link>
          )}

          {/* Sell CTA */}
          <Link
            href="/sell"
            className="flex items-center gap-1.5 bg-brand-500 hover:bg-brand-600 text-white text-sm font-semibold px-3 py-1.5 rounded-lg transition-colors"
          >
            <Plus size={15} />
            <span className="hidden sm:inline">Sell</span>
          </Link>
        </div>
      </div>
    </nav>
  )
}
