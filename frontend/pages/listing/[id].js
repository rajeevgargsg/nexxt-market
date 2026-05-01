import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import { motion } from 'framer-motion'
import {
  ArrowLeft, MessageCircle, Heart, Share2, Flag, MapPin, Tag,
  Star, Shield, ChevronLeft, ChevronRight, Send, Sparkles,
  ExternalLink, Clock
} from 'lucide-react'
import Navbar from '../../components/Navbar'
import HourlySignals from '../../components/HourlySignals'
import { listingsAPI, messagesAPI, aiAPI } from '../../lib/api'
import toast from 'react-hot-toast'
import { formatDistanceToNow } from 'date-fns'
import Link from 'next/link'

export default function ListingDetail() {
  const router = useRouter()
  const { id } = router.query

  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [imageIdx, setImageIdx] = useState(0)
  const [saved, setSaved] = useState(false)
  const [message, setMessage] = useState('')
  const [sending, setSending] = useState(false)
  const [replySuggestion, setReplySuggestion] = useState(null)
  const [aiOptimized, setAiOptimized] = useState(null)
  const [tab, setTab] = useState('signals') // signals | description | seller

  useEffect(() => {
    if (!id) return
    listingsAPI.getListing(id)
      .then(r => setData(r.data))
      .catch(() => setData(getDemoData(id)))
      .finally(() => setLoading(false))

    // Get reply suggestion
    aiAPI.getReplySuggestion(id, 'buyer')
      .then(r => setReplySuggestion(r.data.suggestion))
      .catch(() => setReplySuggestion("Is this still available? Can we meet today?"))
  }, [id])

  const handleSave = async () => {
    try {
      const r = await listingsAPI.saveListing(id)
      setSaved(r.data.saved)
      toast.success(r.data.saved ? '❤️ Saved to watchlist' : 'Removed from watchlist')
    } catch {
      toast.error('Sign in to save listings')
    }
  }

  const handleSendMessage = async () => {
    if (!message.trim()) return
    setSending(true)
    try {
      await messagesAPI.send({
        listing_id: id,
        receiver_id: data.listing.seller_id,
        content: message,
      })
      toast.success('Message sent!')
      setMessage('')
    } catch {
      toast.error('Sign in to send messages')
    } finally {
      setSending(false)
    }
  }

  const handleBoost = async () => {
    try {
      await listingsAPI.boostListing(id, 'standard')
      toast.success('🚀 Listing boosted for 1 hour!')
    } catch {
      toast.error('Sign in to boost listings')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#080808]">
        <Navbar />
        <div className="max-w-6xl mx-auto px-4 py-8">
          <div className="animate-pulse grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="aspect-[4/3] bg-[#111] rounded-2xl" />
            <div className="space-y-4">
              <div className="h-8 bg-[#111] rounded w-3/4" />
              <div className="h-12 bg-[#111] rounded w-1/2" />
              <div className="h-4 bg-[#111] rounded" />
              <div className="h-4 bg-[#111] rounded w-2/3" />
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!data) return null

  const { listing, signals } = data
  const images = listing.images?.length > 0 ? listing.images : [`https://picsum.photos/seed/${id}/800/600`]
  const timeLeft = signals?.time?.hours_left

  return (
    <>
      <Head>
        <title>{listing.title} — NexxtMarket</title>
      </Head>

      <div className="min-h-screen bg-[#080808]">
        <Navbar />

        <div className="max-w-6xl mx-auto px-4 py-6">
          {/* Back */}
          <button
            onClick={() => router.back()}
            className="flex items-center gap-2 text-[#555] hover:text-[#888] text-sm mb-6 transition-colors"
          >
            <ArrowLeft size={14} />
            Back to listings
          </button>

          <div className="grid grid-cols-1 lg:grid-cols-[1fr_380px] gap-6 lg:gap-8">

            {/* Left: Image + details */}
            <div className="space-y-4">
              {/* Image gallery */}
              <div className="relative rounded-2xl overflow-hidden bg-[#111] border border-[#2a2a2a] aspect-[4/3]">
                <img
                  src={images[imageIdx]}
                  alt={listing.title}
                  className="w-full h-full object-cover"
                  onError={e => e.target.src = `https://picsum.photos/seed/${id}${imageIdx}/800/600`}
                />

                {/* Nav arrows */}
                {images.length > 1 && (
                  <>
                    <button
                      onClick={() => setImageIdx(i => (i - 1 + images.length) % images.length)}
                      className="absolute left-3 top-1/2 -translate-y-1/2 p-2 rounded-full bg-[#111]/80 text-white hover:bg-[#111] transition-colors"
                    >
                      <ChevronLeft size={16} />
                    </button>
                    <button
                      onClick={() => setImageIdx(i => (i + 1) % images.length)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 p-2 rounded-full bg-[#111]/80 text-white hover:bg-[#111] transition-colors"
                    >
                      <ChevronRight size={16} />
                    </button>
                    <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-1.5">
                      {images.map((_, i) => (
                        <button
                          key={i}
                          onClick={() => setImageIdx(i)}
                          className={`w-1.5 h-1.5 rounded-full transition-all ${i === imageIdx ? 'bg-white w-4' : 'bg-white/40'}`}
                        />
                      ))}
                    </div>
                  </>
                )}

                {/* Badges */}
                <div className="absolute top-3 left-3 flex flex-col gap-2">
                  {listing.is_boosted && (
                    <span className="deal-badge">🚀 Boosted</span>
                  )}
                  {listing.ai_deal_score >= 70 && (
                    <span className="deal-badge">🔥 Hot Deal</span>
                  )}
                </div>
              </div>

              {/* Tab navigation */}
              <div className="flex border-b border-[#1e1e1e] gap-1">
                {['signals', 'description', 'seller'].map(t => (
                  <button
                    key={t}
                    onClick={() => setTab(t)}
                    className={`px-4 py-2 text-sm font-medium capitalize transition-colors border-b-2 -mb-px ${
                      tab === t
                        ? 'text-brand-500 border-brand-500'
                        : 'text-[#555] border-transparent hover:text-[#888]'
                    }`}
                  >
                    {t === 'signals' ? '⚡ Live Signals' : t === 'description' ? '📋 Details' : '👤 Seller'}
                  </button>
                ))}
              </div>

              {/* Tab content */}
              {tab === 'description' && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="space-y-4"
                >
                  <p className="text-[#a0a0a0] leading-relaxed text-sm">{listing.description}</p>

                  {/* Attributes */}
                  <div className="grid grid-cols-2 gap-2">
                    {[
                      { label: 'Condition', value: listing.condition },
                      { label: 'Location', value: listing.location },
                      { label: 'Category', value: listing.category_id },
                      { label: 'Listed', value: listing.created_at ? formatDistanceToNow(new Date(listing.created_at), { addSuffix: true }) : '-' },
                    ].map(a => a.value && (
                      <div key={a.label} className="bg-[#111] border border-[#1e1e1e] rounded-lg p-3">
                        <p className="text-[10px] text-[#555] uppercase tracking-wider mb-1">{a.label}</p>
                        <p className="text-sm text-[#e8e8e8] font-medium">{a.value}</p>
                      </div>
                    ))}
                  </div>

                  {/* AI tags */}
                  {listing.tags?.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {listing.tags.map(tag => (
                        <span key={tag} className="flex items-center gap-1 bg-[#1a1a1a] border border-[#2a2a2a] text-[#888] text-xs px-2 py-1 rounded-lg">
                          <Tag size={10} />
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </motion.div>
              )}

              {tab === 'signals' && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                  {/* Mobile signals */}
                  <div className="lg:hidden">
                    <HourlySignals signals={signals} onBoost={handleBoost} />
                  </div>
                  {/* Desktop: shown in right column */}
                  <div className="hidden lg:block text-[#555] text-sm">
                    ↗ Live signals shown in the right panel
                  </div>
                </motion.div>
              )}

              {tab === 'seller' && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                  <div className="bg-[#111] border border-[#2a2a2a] rounded-xl p-4">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-10 h-10 rounded-full bg-[#1a1a1a] border border-[#2a2a2a] flex items-center justify-center">
                        <span className="text-lg">👤</span>
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-[#e8e8e8]">Seller</p>
                        <div className="flex items-center gap-2">
                          <Shield size={11} className="text-green-400" />
                          <span className="text-[11px] text-green-400">Verified seller</span>
                        </div>
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-center">
                      <div>
                        <p className="text-brand-500 font-bold text-lg">4.8</p>
                        <p className="text-[10px] text-[#555]">Rating</p>
                      </div>
                      <div>
                        <p className="text-[#e8e8e8] font-bold text-lg">23</p>
                        <p className="text-[10px] text-[#555]">Sales</p>
                      </div>
                      <div>
                        <p className="text-[#e8e8e8] font-bold text-lg">1h</p>
                        <p className="text-[10px] text-[#555]">Response</p>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </div>

            {/* Right: Sticky panel */}
            <div className="lg:sticky lg:top-24 space-y-4 h-fit">
              {/* Price + title */}
              <div className="bg-[#111] border border-[#2a2a2a] rounded-2xl p-5">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="price-tag text-3xl text-brand-500">${listing.price?.toLocaleString()}</p>
                    {listing.market_avg_price && (
                      <p className="text-[11px] text-[#555] mt-0.5">
                        Market avg: ${listing.market_avg_price?.toLocaleString()}
                      </p>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <button onClick={handleSave} className="p-2 rounded-xl bg-[#1a1a1a] hover:bg-[#222] transition-colors">
                      <Heart size={16} className={saved ? 'text-red-400 fill-current' : 'text-[#888]'} />
                    </button>
                    <button className="p-2 rounded-xl bg-[#1a1a1a] hover:bg-[#222] transition-colors">
                      <Share2 size={16} className="text-[#888]" />
                    </button>
                  </div>
                </div>

                <h1 className="text-lg font-semibold text-[#f0f0f0] leading-snug mb-3">{listing.title}</h1>

                <div className="flex items-center gap-3 text-[11px] text-[#555]">
                  {listing.location && (
                    <span className="flex items-center gap-1">
                      <MapPin size={10} />
                      {listing.location}
                    </span>
                  )}
                  {listing.condition && (
                    <span className="flex items-center gap-1">
                      <Tag size={10} />
                      {listing.condition}
                    </span>
                  )}
                  {timeLeft && (
                    <span className="flex items-center gap-1 text-amber-500">
                      <Clock size={10} />
                      {timeLeft.toFixed(0)}h left
                    </span>
                  )}
                </div>
              </div>

              {/* Message box */}
              <div className="bg-[#111] border border-[#2a2a2a] rounded-2xl p-4 space-y-3">
                <p className="text-xs font-semibold text-[#888] uppercase tracking-wider">Contact Seller</p>

                {/* AI suggestion */}
                {replySuggestion && (
                  <button
                    onClick={() => setMessage(replySuggestion)}
                    className="w-full text-left bg-[#1a1a1a] border border-[#2a2a2a] hover:border-purple-500/30 rounded-xl p-3 transition-colors"
                  >
                    <div className="flex items-center gap-1.5 text-purple-400 text-[10px] font-bold uppercase mb-1">
                      <Sparkles size={10} />
                      AI Suggested
                    </div>
                    <p className="text-xs text-[#a0a0a0]">"{replySuggestion}"</p>
                  </button>
                )}

                <textarea
                  value={message}
                  onChange={e => setMessage(e.target.value)}
                  placeholder="Hi, is this still available?"
                  rows={3}
                  className="w-full bg-[#1a1a1a] border border-[#2a2a2a] rounded-xl p-3 text-sm text-[#e8e8e8] placeholder:text-[#444] outline-none resize-none focus:border-brand-500/40 transition-colors"
                />

                <button
                  onClick={handleSendMessage}
                  disabled={sending || !message.trim()}
                  className="w-full flex items-center justify-center gap-2 bg-brand-500 hover:bg-brand-600 disabled:opacity-50 text-white font-semibold py-3 rounded-xl transition-colors"
                >
                  <MessageCircle size={16} />
                  {sending ? 'Sending...' : 'Send Message'}
                </button>
              </div>

              {/* Live signals panel */}
              <div className="hidden lg:block bg-[#111] border border-[#2a2a2a] rounded-2xl p-4">
                <HourlySignals signals={signals} onBoost={handleBoost} />
              </div>

              {/* Report */}
              <button className="w-full flex items-center justify-center gap-2 text-[#333] hover:text-[#555] text-xs transition-colors py-2">
                <Flag size={11} />
                Report this listing
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

// Demo data for when API isn't running
function getDemoData(id) {
  return {
    listing: {
      id,
      title: 'iPhone 14 Pro 256GB Space Black — Excellent Condition',
      description: 'Selling my iPhone 14 Pro in excellent condition. Used for 8 months, no scratches or dents. Comes with original box, cable, and 6 months Apple warranty remaining. Price is slightly negotiable for serious buyers. Local pickup preferred but can arrange delivery.',
      price: 980,
      market_avg_price: 1050,
      location: 'Tampines, Singapore',
      condition: 'Like New',
      images: [`https://picsum.photos/seed/${id}/800/600`, `https://picsum.photos/seed/${id}2/800/600`],
      tags: ['iPhone', 'Apple', 'Smartphone', 'iOS', '5G'],
      status: 'active',
      total_views: 127,
      saves_count: 14,
      messages_count: 6,
      active_buyers: 2,
      is_boosted: false,
      ai_deal_score: 75,
      expires_at: new Date(Date.now() + 18 * 3600000).toISOString(),
      created_at: new Date(Date.now() - 6 * 3600000).toISOString(),
      seller_id: 'seller-1',
    },
    signals: {
      price: {
        type: 'good_deal',
        message: '7% below market average — strong buy signal',
        diff_pct: -7,
        market_avg: 1050,
        suggested_action: 'Buy now — likely to sell today',
        percentile: 22,
      },
      time: {
        urgency: 'high',
        message: '🔥 18 hours remaining — visibility dropping',
        hours_left: 18,
        in_peak_window: true,
        expires_at: new Date(Date.now() + 18 * 3600000).toISOString(),
      },
      social: {
        message: '8 users viewed in the last hour',
        level: 'high',
        views_last_hour: 8,
        total_views: 127,
        saves_count: 14,
        messages_count: 6,
      },
      competition: {
        message: '2 buyers currently negotiating',
        level: 'high',
        active_buyers: 2,
        fomo_score: 78,
      },
      content: {
        message: 'iPhones with warranty sell 40% faster — this one has 6 months remaining.',
        angle: 'warranty value',
      },
      boost_window: {
        active: false,
        message: '⚡ Peak traffic window — boost for 10x more views',
        cta: 'Boost for $0.99',
        opportunity: 'peak_window',
      },
      generated_at: new Date().toISOString(),
    }
  }
}
