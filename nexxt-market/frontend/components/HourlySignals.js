/**
 * HourlySignals — The core UI panel showing all engagement signals for a listing.
 * This is what makes users return. Real data. Real urgency. Real decisions.
 */
import { useState, useEffect } from 'react'
import {
  TrendingUp, TrendingDown, Clock, Users, Eye, Heart, MessageCircle,
  Zap, AlertTriangle, CheckCircle, Info, ChevronRight, Sparkles
} from 'lucide-react'
import clsx from 'clsx'
import { formatDistanceToNow } from 'date-fns'

// ─── Signal renderers ──────────────────────────────────────────────────────────

function PriceSignal({ signal }) {
  if (!signal) return null
  const icons = {
    excellent_deal: <TrendingDown size={15} className="text-green-400" />,
    good_deal: <TrendingDown size={15} className="text-green-400" />,
    fair_price: <CheckCircle size={15} className="text-blue-400" />,
    slightly_high: <TrendingUp size={15} className="text-amber-400" />,
    overpriced: <TrendingUp size={15} className="text-red-400" />,
  }
  const colors = {
    excellent_deal: 'border-green-500/30 bg-green-500/5',
    good_deal: 'border-green-500/20 bg-green-500/5',
    fair_price: 'border-blue-500/20 bg-blue-500/5',
    slightly_high: 'border-amber-500/20 bg-amber-500/5',
    overpriced: 'border-red-500/20 bg-red-500/5',
  }

  return (
    <div className={clsx('signal-card', colors[signal.type])}>
      <div className="flex items-start gap-2.5">
        {icons[signal.type]}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[11px] font-bold text-[#888] uppercase tracking-wider">Price Intelligence</span>
          </div>
          <p className="text-sm text-[#e8e8e8] leading-snug">{signal.message}</p>
          {signal.suggested_action && (
            <p className="text-[11px] text-brand-400 mt-1.5 font-medium flex items-center gap-1">
              <ChevronRight size={10} />
              {signal.suggested_action}
            </p>
          )}
          {signal.market_avg && (
            <p className="text-[10px] text-[#555] mt-1">
              Market avg: ${signal.market_avg?.toFixed(0)} · {signal.diff_pct > 0 ? '+' : ''}{signal.diff_pct?.toFixed(1)}% vs similar
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

function TimeSignal({ signal }) {
  if (!signal) return null
  const [, setTick] = useState(0)

  // Update every minute
  useEffect(() => {
    const t = setInterval(() => setTick(n => n + 1), 60000)
    return () => clearInterval(t)
  }, [])

  const urgencyStyle = {
    critical: 'border-red-500/40 bg-red-500/5',
    high: 'border-amber-500/30 bg-amber-500/5',
    medium: 'border-blue-500/20 bg-blue-500/5',
    low: 'border-[#2a2a2a]',
  }[signal.urgency] || 'border-[#2a2a2a]'

  return (
    <div className={clsx('signal-card', urgencyStyle)}>
      <div className="flex items-start gap-2.5">
        <Clock size={15} className={clsx({
          'text-red-400': signal.urgency === 'critical',
          'text-amber-400': signal.urgency === 'high',
          'text-blue-400': signal.urgency === 'medium',
          'text-[#555]': signal.urgency === 'low',
        })} />
        <div className="flex-1">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[11px] font-bold text-[#888] uppercase tracking-wider">Time Pressure</span>
            {signal.urgency === 'critical' && <span className="urgent-dot" />}
          </div>
          <p className="text-sm text-[#e8e8e8] leading-snug">{signal.message}</p>
          {signal.in_peak_window && (
            <span className="inline-flex items-center gap-1 mt-1.5 text-[10px] text-amber-400 font-semibold">
              <Zap size={9} fill="currentColor" />
              PEAK TRAFFIC WINDOW
            </span>
          )}
        </div>
      </div>
    </div>
  )
}

function SocialSignal({ signal }) {
  if (!signal) return null
  return (
    <div className="signal-card">
      <div className="flex items-start gap-2.5">
        <Eye size={15} className="text-brand-500" />
        <div className="flex-1">
          <span className="text-[11px] font-bold text-[#888] uppercase tracking-wider block mb-1">Social Proof</span>
          <p className="text-sm text-[#e8e8e8] leading-snug">{signal.message}</p>
          <div className="flex items-center gap-4 mt-2">
            <div className="flex items-center gap-1 text-[#555]">
              <Eye size={11} />
              <span className="text-[10px]">{signal.total_views} total views</span>
            </div>
            <div className="flex items-center gap-1 text-[#555]">
              <Heart size={11} />
              <span className="text-[10px]">{signal.saves_count} saves</span>
            </div>
            <div className="flex items-center gap-1 text-[#555]">
              <MessageCircle size={11} />
              <span className="text-[10px]">{signal.messages_count} messages</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function CompetitionSignal({ signal }) {
  if (!signal) return null
  const levelStyle = {
    high: 'border-red-500/30 bg-red-500/5',
    medium: 'border-amber-500/20 bg-amber-500/5',
    low: 'border-[#2a2a2a]',
  }[signal.level] || 'border-[#2a2a2a]'

  // FOMO bar
  const fomoWidth = `${signal.fomo_score || 0}%`

  return (
    <div className={clsx('signal-card', levelStyle)}>
      <div className="flex items-start gap-2.5">
        <Users size={15} className={clsx({
          'text-red-400': signal.level === 'high',
          'text-amber-400': signal.level === 'medium',
          'text-[#555]': signal.level === 'low',
        })} />
        <div className="flex-1">
          <span className="text-[11px] font-bold text-[#888] uppercase tracking-wider block mb-1">Competition</span>
          <p className="text-sm text-[#e8e8e8] leading-snug">{signal.message}</p>
          {signal.fomo_score > 0 && (
            <div className="mt-2">
              <div className="flex justify-between text-[10px] text-[#555] mb-1">
                <span>Competition level</span>
                <span>{signal.fomo_score}/100</span>
              </div>
              <div className="h-1 bg-[#1a1a1a] rounded-full overflow-hidden">
                <div
                  className={clsx('h-full rounded-full transition-all duration-500', {
                    'bg-red-500': signal.fomo_score >= 70,
                    'bg-amber-500': signal.fomo_score >= 40 && signal.fomo_score < 70,
                    'bg-green-500': signal.fomo_score < 40,
                  })}
                  style={{ width: fomoWidth }}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function ContentInsight({ signal }) {
  if (!signal) return null
  return (
    <div className="signal-card">
      <div className="flex items-start gap-2.5">
        <Sparkles size={15} className="text-purple-400" />
        <div className="flex-1">
          <span className="text-[11px] font-bold text-[#888] uppercase tracking-wider block mb-1">AI Insight</span>
          <p className="text-sm text-[#e8e8e8] leading-snug italic">{signal.message}</p>
          <span className="text-[10px] text-[#444] mt-1 block">Updated hourly by AI</span>
        </div>
      </div>
    </div>
  )
}

function BoostWindow({ signal, onBoost }) {
  if (!signal) return null
  return (
    <div className={clsx('signal-card', signal.active ? 'border-brand-500/40 bg-brand-500/5' : 'border-[#2a2a2a]')}>
      <div className="flex items-center gap-2.5">
        <Zap size={15} className="text-brand-500" fill={signal.active ? 'currentColor' : 'none'} />
        <div className="flex-1">
          <p className="text-sm text-[#e8e8e8]">{signal.message}</p>
          {signal.expires_in_mins && (
            <span className="text-[10px] text-brand-400">Expires in {signal.expires_in_mins}m</span>
          )}
        </div>
        {!signal.active && signal.cta && (
          <button
            onClick={onBoost}
            className="text-[11px] font-bold bg-brand-500 hover:bg-brand-600 text-white px-3 py-1.5 rounded-lg transition-colors whitespace-nowrap"
          >
            {signal.cta}
          </button>
        )}
      </div>
    </div>
  )
}

// ─── Main Component ───────────────────────────────────────────────────────────

export default function HourlySignals({ signals, isSellerView = false, onBoost }) {
  const [expanded, setExpanded] = useState(true)

  if (!signals) {
    return (
      <div className="animate-pulse space-y-3">
        {[1,2,3].map(i => (
          <div key={i} className="h-16 bg-[#111] rounded-xl border border-[#2a2a2a]" />
        ))}
      </div>
    )
  }

  const generatedAt = signals.generated_at
    ? formatDistanceToNow(new Date(signals.generated_at), { addSuffix: true })
    : ''

  return (
    <div className="space-y-2">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="live-badge">
            <span className="urgent-dot" style={{width:6, height:6}} />
            LIVE SIGNALS
          </div>
          <span className="text-[10px] text-[#444]">Updated {generatedAt}</span>
        </div>
        <button
          onClick={() => setExpanded(e => !e)}
          className="text-[11px] text-[#555] hover:text-[#888] transition-colors"
        >
          {expanded ? 'Collapse' : 'Expand'}
        </button>
      </div>

      {expanded && (
        <div className="space-y-2">
          {/* Time pressure — always first if urgent */}
          {signals.time && signals.time.urgency !== 'low' && (
            <TimeSignal signal={signals.time} />
          )}

          {/* Price intelligence */}
          <PriceSignal signal={signals.price} />

          {/* Competition */}
          <CompetitionSignal signal={signals.competition} />

          {/* Social proof */}
          <SocialSignal signal={signals.social} />

          {/* Content insight */}
          <ContentInsight signal={signals.content} />

          {/* Time pressure if low urgency */}
          {signals.time && signals.time.urgency === 'low' && (
            <TimeSignal signal={signals.time} />
          )}

          {/* Boost window */}
          {signals.boost_window && (
            <BoostWindow signal={signals.boost_window} onBoost={onBoost} />
          )}

          {/* Seller nudge — only in seller view */}
          {isSellerView && signals.seller_nudge && (
            <div className="signal-card border-amber-500/20 bg-amber-500/5">
              <div className="flex items-start gap-2.5">
                <AlertTriangle size={15} className="text-amber-400" />
                <div>
                  <span className="text-[11px] font-bold text-[#888] uppercase tracking-wider block mb-1">Action Required</span>
                  <p className="text-sm text-[#e8e8e8]">{signals.seller_nudge.message}</p>
                  {signals.seller_nudge.impact && (
                    <span className="text-[10px] text-amber-400 font-semibold mt-1 block">
                      Expected impact: {signals.seller_nudge.impact}
                    </span>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
