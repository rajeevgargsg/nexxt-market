import { useState, useEffect, useCallback } from 'react'
import Head from 'next/head'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Flame, Clock, TrendingUp, Grid, LayoutList, SlidersHorizontal, ChevronDown,
  Zap, Search, Tag, MapPin, RefreshCw
} from 'lucide-react'
import Navbar from '../components/Navbar'
import ListingCard from '../components/ListingCard'
import { listingsAPI } from '../lib/api'
import toast from 'react-hot-toast'

const CATEGORIES = [
  { id: 'all', label: 'All', icon: '✦' },
  { id: 'electronics', label: 'Electronics', icon: '📱' },
  { id: 'vehicles', label: 'Vehicles', icon: '🚗' },
  { id: 'furniture', label: 'Furniture', icon: '🛋️' },
  { id: 'fashion', label: 'Fashion', icon: '👗' },
  { id: 'sports', label: 'Sports', icon: '⚽' },
  { id: 'books', label: 'Books', icon: '📚' },
  { id: 'property', label: 'Property', icon: '🏠' },
]

const SORTS = [
  { value: 'rank', label: '🔥 Trending', icon: Flame },
  { value: 'newest', label: '⚡ Newest', icon: Zap },
  { value: 'price_asc', label: '↑ Price', icon: TrendingUp },
  { value: 'price_desc', label: '↓ Price', icon: TrendingUp },
]

// Ticker feed — shows real-time activity
const TICKER_EVENTS = [
  '⚡ iPhone 14 Pro sold in Singapore',
  '🔥 3 buyers competing for Honda Civic',
  '💰 MacBook reduced by $200 — 8% below market',
  '👀 Nike Air Max: 14 views in last hour',
  '⏰ 2h left on featured Samsung TV',
  '🏆 New seller verified: ElectroHub SG',
  '🔥 IKEA sofa: 5 users watching',
  '💬 Deal closed: Canon camera sold in 3h',
]

export default function Home() {
  const [listings, setListings] = useState([])
  const [loading, setLoading] = useState(true)
  const [category, setCategory] = useState('all')
  const [sort, setSort] = useState('rank')
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const fetchListings = useCallback(async (reset = false) => {
    try {
      setLoading(true)
      const params = {
        sort,
        page: reset ? 1 : page,
        limit: 20,
      }
      if (category !== 'all') params.category = category

      const r = await listingsAPI.getFeed(params)
      const newListings = r.data

      if (reset) {
        setListings(newListings)
        setPage(1)
      } else {
        setListings(prev => [...prev, ...newListings])
      }

      setHasMore(newListings.length === 20)
    } catch (err) {
      // Show demo data if API not running
      setListings(generateDemoListings())
      setHasMore(false)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [category, sort, page])

  useEffect(() => {
    fetchListings(true)
  }, [category, sort])

  const handleRefresh = () => {
    setRefreshing(true)
    fetchListings(true)
    toast.success('Feed refreshed with latest listings')
  }

  return (
    <>
      <Head>
        <title>NexxtMarket — Buy & Sell Smarter</title>
        <meta name="description" content="AI-powered marketplace with real-time signals. Listings that evolve every hour." />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-[#080808]">
        <Navbar />

        {/* Ticker bar */}
        <div className="bg-[#0e0e0e] border-b border-[#1a1a1a] overflow-hidden h-8 flex items-center">
          <div className="shrink-0 px-3 text-[10px] font-bold text-brand-500 uppercase tracking-widest border-r border-[#2a2a2a] mr-3 h-full flex items-center">
            LIVE
          </div>
          <div className="overflow-hidden flex-1">
            <div className="flex gap-12 animate-ticker whitespace-nowrap">
              {[...TICKER_EVENTS, ...TICKER_EVENTS].map((event, i) => (
                <span key={i} className="text-[11px] text-[#555] shrink-0">{event}</span>
              ))}
            </div>
          </div>
        </div>

        {/* Hero */}
        <div className="bg-gradient-to-b from-[#0f0f0f] to-[#080808] border-b border-[#1a1a1a] px-4 py-8">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-center mb-6"
            >
              <h1 className="font-display text-5xl md:text-7xl tracking-wider mb-2">
                <span className="text-gradient">NEXXT</span>
                <span className="text-[#333]">MARKET</span>
              </h1>
              <p className="text-[#555] text-sm md:text-base max-w-lg mx-auto">
                Every listing evolves every hour. Real signals. Real urgency. Real decisions.
              </p>
            </motion.div>

            {/* Search */}
            <div className="max-w-2xl mx-auto">
              <div className="flex items-center gap-2 bg-[#111] border border-[#2a2a2a] rounded-xl px-4 h-12 focus-within:border-brand-500/50 transition-colors">
                <Search size={16} className="text-[#555] shrink-0" />
                <input
                  type="text"
                  placeholder="Search for anything..."
                  className="flex-1 bg-transparent text-[#f0f0f0] placeholder:text-[#333] outline-none text-sm"
                />
                <button className="shrink-0 bg-brand-500 hover:bg-brand-600 text-white text-sm font-semibold px-4 py-1.5 rounded-lg transition-colors">
                  Search
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="sticky top-14 z-40 bg-[#080808]/95 backdrop-blur-sm border-b border-[#1a1a1a]">
          <div className="max-w-7xl mx-auto px-4">
            {/* Categories */}
            <div className="flex items-center gap-1 overflow-x-auto py-3 scrollbar-hide">
              {CATEGORIES.map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => setCategory(cat.id)}
                  className={`shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                    category === cat.id
                      ? 'bg-brand-500 text-white'
                      : 'text-[#666] hover:text-[#e8e8e8] hover:bg-[#1a1a1a]'
                  }`}
                >
                  <span>{cat.icon}</span>
                  <span>{cat.label}</span>
                </button>
              ))}
            </div>

            {/* Sort + filters */}
            <div className="flex items-center justify-between pb-3">
              <div className="flex items-center gap-2">
                {SORTS.map((s) => (
                  <button
                    key={s.value}
                    onClick={() => setSort(s.value)}
                    className={`text-xs px-2.5 py-1 rounded-md font-medium transition-all ${
                      sort === s.value
                        ? 'bg-[#1a1a1a] text-[#f0f0f0] border border-[#333]'
                        : 'text-[#555] hover:text-[#888]'
                    }`}
                  >
                    {s.label}
                  </button>
                ))}
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={handleRefresh}
                  className="flex items-center gap-1.5 text-[#555] hover:text-[#888] text-xs transition-colors"
                >
                  <RefreshCw size={12} className={refreshing ? 'animate-spin' : ''} />
                  <span className="hidden sm:inline">Refresh</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Main content */}
        <main className="max-w-7xl mx-auto px-4 py-6">

          {/* Stats bar */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
            {[
              { label: 'Active Listings', value: '2,847', icon: '📋', color: 'text-brand-500' },
              { label: 'Sold Today', value: '143', icon: '✅', color: 'text-green-400' },
              { label: 'Live Negotiations', value: '38', icon: '⚡', color: 'text-amber-400' },
              { label: 'Expiring Soon', value: '12', icon: '⏰', color: 'text-red-400' },
            ].map((stat, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className="bg-[#111] border border-[#1e1e1e] rounded-xl p-3"
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-base">{stat.icon}</span>
                  <span className={`font-display text-2xl tracking-wide ${stat.color}`}>{stat.value}</span>
                </div>
                <p className="text-[11px] text-[#555]">{stat.label}</p>
              </motion.div>
            ))}
          </div>

          {/* Listings grid */}
          {loading && listings.length === 0 ? (
            <div className="listings-grid">
              {Array.from({ length: 12 }).map((_, i) => (
                <div key={i} className="bg-[#111] border border-[#1e1e1e] rounded-xl overflow-hidden animate-pulse">
                  <div className="aspect-[4/3] bg-[#1a1a1a]" />
                  <div className="p-3 space-y-2">
                    <div className="h-5 bg-[#1a1a1a] rounded w-2/3" />
                    <div className="h-4 bg-[#1a1a1a] rounded w-full" />
                    <div className="h-3 bg-[#1a1a1a] rounded w-1/2" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <>
              <div className="listings-grid">
                <AnimatePresence>
                  {listings.map((listing, i) => (
                    <motion.div
                      key={listing.id}
                      initial={{ opacity: 0, y: 12 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: Math.min(i * 0.03, 0.3) }}
                    >
                      <ListingCard listing={listing} signals={listing.signals} />
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>

              {/* Load more */}
              {hasMore && (
                <div className="text-center mt-8">
                  <button
                    onClick={() => { setPage(p => p + 1); fetchListings() }}
                    className="bg-[#111] border border-[#2a2a2a] hover:border-brand-500/40 text-[#888] hover:text-white px-6 py-2.5 rounded-xl text-sm font-medium transition-all"
                  >
                    Load more listings
                  </button>
                </div>
              )}

              {listings.length === 0 && !loading && (
                <div className="text-center py-20">
                  <p className="text-5xl mb-4">🔍</p>
                  <p className="text-[#555] text-lg font-medium">No listings found</p>
                  <p className="text-[#333] text-sm mt-1">Be the first to sell in this category</p>
                </div>
              )}
            </>
          )}
        </main>

        {/* Footer */}
        <footer className="border-t border-[#1a1a1a] mt-16 py-8 px-4 text-center text-[#333] text-xs">
          <p>NexxtMarket — AI-Driven Classified Marketplace · MIT License</p>
          <p className="mt-1">Built with Next.js, FastAPI, Groq AI, PostgreSQL · <a href="https://github.com" className="hover:text-brand-500 transition-colors">View on GitHub</a></p>
        </footer>
      </div>
    </>
  )
}

// ─── Demo data generator ───────────────────────────────────────────────────────
function generateDemoListings() {
  const titles = [
    'iPhone 14 Pro 256GB Space Black',
    'Honda Civic 2020 - Low Mileage',
    'MacBook Pro M2 - Like New',
    'IKEA KALLAX Shelf Unit',
    'Sony WH-1000XM5 Headphones',
    'PS5 + 3 Games Bundle',
    'Nike Air Jordan 1 Retro High',
    'Canon EOS R50 Camera Kit',
    'Samsung 65" QLED 4K TV',
    'Standing Desk + Ergonomic Chair',
    'Dyson V15 Vacuum',
    'Apple Watch Series 9',
  ]

  return titles.map((title, i) => ({
    id: `demo-${i}`,
    title,
    price: Math.floor(Math.random() * 2000) + 100,
    location: ['Tampines', 'Orchard', 'Jurong', 'Bishan', 'Clementi'][i % 5],
    condition: ['Like New', 'Good', 'Excellent', 'Fair'][i % 4],
    images: [`https://picsum.photos/seed/${i+10}/400/300`],
    status: 'active',
    total_views: Math.floor(Math.random() * 200) + 5,
    saves_count: Math.floor(Math.random() * 20),
    messages_count: Math.floor(Math.random() * 10),
    active_buyers: Math.floor(Math.random() * 4),
    is_boosted: i % 7 === 0,
    ai_deal_score: Math.floor(Math.random() * 60) + 20,
    market_avg_price: Math.floor(Math.random() * 2000) + 100,
    expires_at: new Date(Date.now() + (Math.random() * 72 * 3600000)).toISOString(),
    created_at: new Date(Date.now() - (Math.random() * 24 * 3600000)).toISOString(),
    seller_id: `seller-${i % 5}`,
    signals: {
      time: {
        urgency: ['low','medium','high','critical'][Math.floor(Math.random() * 4)],
        hours_left: Math.random() * 48,
        message: '🔥 High interest — 12h remaining',
        in_peak_window: Math.random() > 0.5,
      },
      competition: {
        level: ['low','medium','high'][Math.floor(Math.random() * 3)],
        active_buyers: Math.floor(Math.random() * 4),
        fomo_score: Math.floor(Math.random() * 90),
        message: '2 buyers currently interested',
      },
      price: {
        type: ['good_deal','fair_price','excellent_deal'][Math.floor(Math.random() * 3)],
        diff_pct: (Math.random() - 0.5) * 30,
        message: '12% below market average',
        market_avg: Math.floor(Math.random() * 2000) + 100,
      },
    }
  }))
}
