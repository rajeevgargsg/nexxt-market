import { useState, useEffect } from 'react'
import Head from 'next/head'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { motion } from 'framer-motion'
import {
  Package, TrendingUp, Eye, MessageCircle, Heart,
  Clock, Zap, Plus, Edit, Trash2, BarChart2,
  Star, DollarSign, Activity
} from 'lucide-react'
import Navbar from '../components/Navbar'
import { api } from '../lib/api'
import toast from 'react-hot-toast'

const DEMO_LISTINGS = [
  {
    id: 1, title: 'Sony WH-1000XM4 Headphones', price: 180, status: 'active',
    views: 247, saves: 18, messages: 7, ai_deal_score: 82,
    expires_at: new Date(Date.now() + 4 * 3600000).toISOString(),
    category: 'Electronics', images: [], rank_score: 91,
  },
  {
    id: 2, title: 'IKEA KALLAX Shelf Unit', price: 65, status: 'active',
    views: 83, saves: 5, messages: 2, ai_deal_score: 61,
    expires_at: new Date(Date.now() + 18 * 3600000).toISOString(),
    category: 'Furniture', images: [], rank_score: 74,
  },
  {
    id: 3, title: 'Trek FX3 City Bike 2022', price: 420, status: 'sold',
    views: 512, saves: 34, messages: 21, ai_deal_score: 94,
    expires_at: new Date(Date.now() - 86400000).toISOString(),
    category: 'Sports', images: [], rank_score: 0,
  },
]

export default function Dashboard() {
  const router = useRouter()
  const [listings, setListings] = useState([])
  const [stats, setStats] = useState({ total: 0, active: 0, totalViews: 0, totalMessages: 0 })
  const [tab, setTab] = useState('active')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
    if (!token) { router.push('/auth'); return }
    loadDashboard(token)
  }, [])

  const loadDashboard = async (token) => {
    try {
      const res = await api.get('/listing/my', {
        headers: { Authorization: `Bearer ${token}` }
      })
      const data = res.data?.listings || DEMO_LISTINGS
      setListings(data)
      computeStats(data)
    } catch {
      setListings(DEMO_LISTINGS)
      computeStats(DEMO_LISTINGS)
    } finally {
      setLoading(false)
    }
  }

  const computeStats = (data) => {
    setStats({
      total: data.length,
      active: data.filter(l => l.status === 'active').length,
      totalViews: data.reduce((s, l) => s + (l.views || 0), 0),
      totalMessages: data.reduce((s, l) => s + (l.messages || 0), 0),
    })
  }

  const filtered = listings.filter(l =>
    tab === 'all' ? true : l.status === tab
  )

  const hoursLeft = (expiresAt) => {
    const diff = new Date(expiresAt) - Date.now()
    if (diff <= 0) return null
    const h = Math.floor(diff / 3600000)
    const m = Math.floor((diff % 3600000) / 60000)
    return h > 0 ? `${h}h ${m}m` : `${m}m`
  }

  return (
    <>
      <Head><title>Dashboard — NexxtMarket</title></Head>
      <div className="min-h-screen bg-[#080808]">
        <Navbar />

        <div className="max-w-6xl mx-auto px-4 py-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="font-bebas text-4xl text-white">MY DASHBOARD</h1>
              <p className="text-white/40 font-dm text-sm mt-1">Manage your listings & track performance</p>
            </div>
            <Link href="/sell">
              <button className="flex items-center gap-2 bg-orange-500 hover:bg-orange-400 text-black font-dm font-bold px-5 py-2.5 rounded-xl transition-all">
                <Plus size={16} /> New Listing
              </button>
            </Link>
          </div>

          {/* Stats row */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {[
              { icon: <Package size={18} />, label: 'Total Listings', value: stats.total, color: 'text-white' },
              { icon: <Activity size={18} />, label: 'Active', value: stats.active, color: 'text-green-400' },
              { icon: <Eye size={18} />, label: 'Total Views', value: stats.totalViews, color: 'text-blue-400' },
              { icon: <MessageCircle size={18} />, label: 'Messages', value: stats.totalMessages, color: 'text-orange-400' },
            ].map((s, i) => (
              <motion.div
                key={s.label}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className="bg-white/5 border border-white/10 rounded-2xl p-5"
              >
                <div className={`${s.color} mb-3`}>{s.icon}</div>
                <div className={`font-bebas text-3xl ${s.color}`}>{s.value}</div>
                <div className="text-white/40 text-xs font-dm mt-1">{s.label}</div>
              </motion.div>
            ))}
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-6">
            {['active', 'sold', 'expired', 'all'].map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`px-4 py-2 rounded-lg text-sm font-dm font-medium capitalize transition-all ${
                  tab === t
                    ? 'bg-orange-500 text-black'
                    : 'bg-white/5 text-white/50 hover:text-white'
                }`}
              >
                {t}
              </button>
            ))}
          </div>

          {/* Listings */}
          {loading ? (
            <div className="grid gap-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-28 bg-white/5 rounded-2xl animate-pulse" />
              ))}
            </div>
          ) : filtered.length === 0 ? (
            <div className="text-center py-20">
              <Package className="text-white/20 mx-auto mb-4" size={48} />
              <p className="text-white/40 font-dm">No {tab} listings yet</p>
              <Link href="/sell">
                <button className="mt-4 px-6 py-2.5 bg-orange-500 text-black font-dm font-bold rounded-xl">
                  Create your first listing
                </button>
              </Link>
            </div>
          ) : (
            <div className="grid gap-4">
              {filtered.map((listing, i) => (
                <motion.div
                  key={listing.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.04 }}
                  className="bg-white/5 border border-white/10 hover:border-white/20 rounded-2xl p-5 transition-all"
                >
                  <div className="flex items-start gap-4">
                    {/* Thumbnail placeholder */}
                    <div className="w-16 h-16 bg-white/10 rounded-xl flex-shrink-0 flex items-center justify-center">
                      <Package className="text-white/30" size={20} />
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <Link href={`/listing/${listing.id}`}>
                            <h3 className="font-dm font-semibold text-white hover:text-orange-400 transition-colors truncate">
                              {listing.title}
                            </h3>
                          </Link>
                          <div className="flex items-center gap-3 mt-1">
                            <span className="font-mono text-orange-400 font-bold">${listing.price}</span>
                            <StatusBadge status={listing.status} />
                            {listing.ai_deal_score && (
                              <span className="text-xs font-dm text-white/40">
                                AI Score: <span className="text-green-400">{listing.ai_deal_score}</span>
                              </span>
                            )}
                          </div>
                        </div>

                        <div className="flex-shrink-0 flex gap-2">
                          <Link href={`/listing/${listing.id}`}>
                            <button className="p-2 bg-white/5 hover:bg-white/10 rounded-lg text-white/50 hover:text-white transition-all">
                              <BarChart2 size={15} />
                            </button>
                          </Link>
                          <button className="p-2 bg-white/5 hover:bg-white/10 rounded-lg text-white/50 hover:text-white transition-all">
                            <Edit size={15} />
                          </button>
                        </div>
                      </div>

                      <div className="flex items-center gap-4 mt-3 flex-wrap">
                        <Metric icon={<Eye size={13} />} value={listing.views || 0} label="views" />
                        <Metric icon={<Heart size={13} />} value={listing.saves || 0} label="saves" />
                        <Metric icon={<MessageCircle size={13} />} value={listing.messages || 0} label="msgs" />
                        {listing.status === 'active' && hoursLeft(listing.expires_at) && (
                          <span className="flex items-center gap-1 text-xs font-dm text-yellow-400">
                            <Clock size={12} />
                            {hoursLeft(listing.expires_at)} left
                          </span>
                        )}
                        {listing.is_boosted && (
                          <span className="flex items-center gap-1 text-xs font-dm text-orange-400">
                            <Zap size={12} />
                            Boosted
                          </span>
                        )}
                      </div>

                      {/* Rank bar */}
                      {listing.status === 'active' && (
                        <div className="mt-3">
                          <div className="flex justify-between text-xs text-white/30 font-dm mb-1">
                            <span>Visibility rank</span>
                            <span>{listing.rank_score?.toFixed(0) || 0}/100</span>
                          </div>
                          <div className="h-1 bg-white/10 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-orange-500 to-yellow-400 rounded-full"
                              style={{ width: `${listing.rank_score || 0}%` }}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  )
}

function Metric({ icon, value, label }) {
  return (
    <span className="flex items-center gap-1 text-xs font-dm text-white/40">
      {icon}
      <span className="text-white/70">{value}</span> {label}
    </span>
  )
}

function StatusBadge({ status }) {
  const map = {
    active: 'bg-green-500/15 text-green-400 border-green-500/30',
    sold: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
    expired: 'bg-red-500/15 text-red-400 border-red-500/30',
  }
  return (
    <span className={`text-xs font-dm px-2 py-0.5 rounded-full border capitalize ${map[status] || 'bg-white/10 text-white/40'}`}>
      {status}
    </span>
  )
}
