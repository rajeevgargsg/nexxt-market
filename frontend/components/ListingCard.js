import Link from 'next/link'
import { formatDistanceToNow } from 'date-fns'
import { Eye, Heart, MessageCircle, Zap, Clock, TrendingUp, Users } from 'lucide-react'
import { useState } from 'react'
import { listingsAPI } from '../lib/api'
import toast from 'react-hot-toast'
import clsx from 'clsx'

function urgencyColor(urgency) {
  return {
    critical: 'text-red-400',
    high: 'text-amber-400',
    medium: 'text-blue-400',
    low: 'text-[#888]',
  }[urgency] || 'text-[#888]'
}

function dealBadge(score) {
  if (score >= 80) return { label: 'HOT DEAL', cls: 'bg-red-500/20 text-red-400 border-red-500/30' }
  if (score >= 60) return { label: 'GOOD DEAL', cls: 'bg-green-500/20 text-green-400 border-green-500/30' }
  if (score >= 40) return { label: 'FAIR PRICE', cls: 'bg-blue-500/20 text-blue-400 border-blue-500/30' }
  return null
}

export default function ListingCard({ listing, signals }) {
  const [saved, setSaved] = useState(false)

  const handleSave = async (e) => {
    e.preventDefault()
    e.stopPropagation()
    try {
      const r = await listingsAPI.saveListing(listing.id)
      setSaved(r.data.saved)
      toast.success(r.data.saved ? 'Saved to watchlist' : 'Removed from watchlist')
    } catch {
      toast.error('Sign in to save listings')
    }
  }

  const timeSignal = signals?.time
  const competitionSignal = signals?.competition
  const priceSignal = signals?.price
  const deal = dealBadge(listing.ai_deal_score)

  const image = listing.images?.[0] || '/placeholder.jpg'
  const timeAgo = listing.created_at ? formatDistanceToNow(new Date(listing.created_at), { addSuffix: true }) : ''

  return (
    <Link href={`/listing/${listing.id}`}>
      <div className="group relative bg-[#111] border border-[#2a2a2a] rounded-xl overflow-hidden hover:border-[#f97316]/40 transition-all duration-200 hover:shadow-lg hover:shadow-[#f97316]/5 cursor-pointer animate-slide-up">

        {/* Image */}
        <div className="relative aspect-[4/3] bg-[#1a1a1a] overflow-hidden">
          <img
            src={image}
            alt={listing.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            onError={(e) => { e.target.src = `https://picsum.photos/seed/${listing.id}/400/300` }}
          />

          {/* Boost badge */}
          {listing.is_boosted && (
            <div className="absolute top-2 left-2 flex items-center gap-1 bg-[#f97316] text-white text-[10px] font-bold px-2 py-1 rounded-md">
              <Zap size={9} fill="white" />
              BOOSTED
            </div>
          )}

          {/* Deal badge */}
          {deal && (
            <div className={clsx('absolute top-2 right-2 text-[10px] font-bold px-2 py-1 rounded-md border', deal.cls)}>
              {deal.label}
            </div>
          )}

          {/* Save button */}
          <button
            onClick={handleSave}
            className={clsx(
              'absolute bottom-2 right-2 p-1.5 rounded-lg backdrop-blur-sm transition-all',
              saved ? 'bg-red-500/80 text-white' : 'bg-[#111]/70 text-[#888] hover:text-red-400'
            )}
          >
            <Heart size={14} fill={saved ? 'currentColor' : 'none'} />
          </button>

          {/* Urgency overlay */}
          {timeSignal?.urgency === 'critical' && (
            <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-red-950/80 to-transparent px-3 py-2">
              <div className="flex items-center gap-1.5">
                <span className="urgent-dot" />
                <span className="text-red-300 text-[11px] font-semibold">{timeSignal.hours_left?.toFixed(0)}h left</span>
              </div>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-3">
          {/* Price */}
          <div className="flex items-start justify-between gap-2 mb-1.5">
            <span className="price-tag text-[#f97316] text-xl">
              ${listing.price?.toLocaleString()}
            </span>
            {listing.market_avg_price && priceSignal?.diff_pct && (
              <span className={clsx(
                'text-[10px] font-semibold px-1.5 py-0.5 rounded',
                priceSignal.diff_pct < -5 ? 'text-green-400 bg-green-500/10' : 'text-[#888] bg-[#1a1a1a]'
              )}>
                {priceSignal.diff_pct > 0 ? '+' : ''}{priceSignal.diff_pct?.toFixed(0)}% vs avg
              </span>
            )}
          </div>

          {/* Title */}
          <h3 className="text-sm font-medium text-[#e8e8e8] line-clamp-2 leading-snug mb-2">
            {listing.title}
          </h3>

          {/* Location + time */}
          <div className="flex items-center justify-between text-[#555] text-[11px] mb-2.5">
            <span>{listing.location || 'Location not set'}</span>
            <span>{timeAgo}</span>
          </div>

          {/* Signal row */}
          <div className="flex items-center gap-3 pt-2.5 border-t border-[#1e1e1e]">
            {/* Views */}
            <div className="flex items-center gap-1 text-[#555]">
              <Eye size={11} />
              <span className="text-[10px]">{listing.total_views || 0}</span>
            </div>

            {/* Saves */}
            <div className="flex items-center gap-1 text-[#555]">
              <Heart size={11} />
              <span className="text-[10px]">{listing.saves_count || 0}</span>
            </div>

            {/* Messages */}
            <div className="flex items-center gap-1 text-[#555]">
              <MessageCircle size={11} />
              <span className="text-[10px]">{listing.messages_count || 0}</span>
            </div>

            {/* Competition signal */}
            {competitionSignal?.level === 'high' && (
              <div className="ml-auto flex items-center gap-1 text-amber-400">
                <Users size={11} />
                <span className="text-[10px] font-semibold">
                  {competitionSignal.active_buyers} interested
                </span>
              </div>
            )}

            {/* Time signal */}
            {timeSignal && timeSignal.urgency !== 'low' && !competitionSignal?.level === 'high' && (
              <div className={clsx('ml-auto flex items-center gap-1', urgencyColor(timeSignal.urgency))}>
                <Clock size={11} />
                <span className="text-[10px] font-semibold">{timeSignal.hours_left?.toFixed(0)}h left</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </Link>
  )
}
