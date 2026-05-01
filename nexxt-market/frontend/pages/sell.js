import { useState } from 'react'
import Head from 'next/head'
import { motion } from 'framer-motion'
import { Sparkles, Upload, X, ChevronRight, CheckCircle, AlertTriangle, Loader } from 'lucide-react'
import Navbar from '../components/Navbar'
import { listingsAPI, aiAPI } from '../lib/api'
import toast from 'react-hot-toast'
import { useRouter } from 'next/router'

const CONDITIONS = ['New', 'Like New', 'Good', 'Fair', 'Poor']
const DURATIONS = [
  { hours: 24, label: '24 hours', note: 'Best for fast sales' },
  { hours: 48, label: '48 hours', note: 'Most popular' },
  { hours: 72, label: '72 hours', note: 'Max exposure' },
]
const CATEGORIES = [
  'Electronics', 'Vehicles', 'Furniture', 'Fashion',
  'Sports', 'Books', 'Property', 'Other'
]

export default function SellPage() {
  const router = useRouter()
  const [form, setForm] = useState({
    title: '',
    description: '',
    price: '',
    category: '',
    location: '',
    condition: 'Good',
    duration_hours: 48,
    images: [],
    tags: [],
  })
  const [step, setStep] = useState(1) // 1=basic, 2=ai optimize, 3=publish
  const [aiResult, setAiResult] = useState(null)
  const [optimizing, setOptimizing] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [useAiVersion, setUseAiVersion] = useState(false)

  const update = (field, value) => setForm(f => ({ ...f, [field]: value }))

  const handleAiOptimize = async () => {
    setOptimizing(true)
    try {
      // Simulate AI optimization (calls backend /ai/optimize-listing)
      // For demo, we'll create the listing first then optimize
      const payload = {
        ...form,
        price: parseFloat(form.price),
      }

      // Mock AI response for demo
      await new Promise(r => setTimeout(r, 1500))
      setAiResult({
        optimized_title: `${form.title} — ${form.condition} Condition | Fast Delivery`,
        optimized_description: `${form.description} This item is in ${form.condition.toLowerCase()} condition and ready for immediate sale. Local pickup available. Price is competitive with current market rates.`,
        suggested_tags: form.category ? [form.category, form.condition, 'FastSale', 'Negotiable'] : ['ForSale', form.condition],
        suggested_price: parseFloat(form.price) * (0.95 + Math.random() * 0.1),
        deal_score: Math.floor(Math.random() * 30) + 55,
        conversion_probability: 'high',
        weak_points: form.images.length < 3 ? ['Add more photos for better visibility'] : [],
        strong_points: ['Competitive pricing', 'Good condition stated'],
      })
      setStep(2)
    } catch (err) {
      toast.error('AI optimization failed — you can still publish')
      setStep(3)
    } finally {
      setOptimizing(false)
    }
  }

  const handlePublish = async () => {
    setSubmitting(true)
    try {
      const payload = {
        title: useAiVersion && aiResult ? aiResult.optimized_title : form.title,
        description: useAiVersion && aiResult ? aiResult.optimized_description : form.description,
        price: parseFloat(form.price),
        category_id: form.category?.toLowerCase(),
        location: form.location,
        condition: form.condition,
        duration_hours: form.duration_hours,
        images: form.images,
        tags: useAiVersion && aiResult ? aiResult.suggested_tags : form.tags,
      }

      const r = await listingsAPI.createListing(payload)
      toast.success('🎉 Listing published!')
      router.push(`/listing/${r.data.id}`)
    } catch (err) {
      // Demo: redirect to home
      toast.success('🎉 Listing published! (Demo mode)')
      router.push('/')
    } finally {
      setSubmitting(false)
    }
  }

  const canOptimize = form.title && form.description && form.price && form.category

  return (
    <>
      <Head><title>Sell — NexxtMarket</title></Head>
      <div className="min-h-screen bg-[#080808]">
        <Navbar />

        <div className="max-w-2xl mx-auto px-4 py-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="font-display text-4xl text-gradient mb-1">SELL FAST</h1>
            <p className="text-[#555] text-sm">AI-optimized listings sell 3x faster</p>
          </div>

          {/* Progress */}
          <div className="flex items-center gap-2 mb-8">
            {[1,2,3].map(s => (
              <div key={s} className="flex items-center gap-2">
                <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-colors ${
                  step >= s ? 'bg-brand-500 text-white' : 'bg-[#1a1a1a] text-[#555] border border-[#2a2a2a]'
                }`}>
                  {step > s ? <CheckCircle size={14} /> : s}
                </div>
                {s < 3 && <div className={`flex-1 h-0.5 w-12 ${step > s ? 'bg-brand-500' : 'bg-[#2a2a2a]'}`} />}
              </div>
            ))}
            <div className="flex gap-8 ml-2 text-[11px] text-[#555]">
              <span className={step === 1 ? 'text-brand-500' : ''}>Details</span>
              <span className={step === 2 ? 'text-brand-500' : ''}>AI Optimize</span>
              <span className={step === 3 ? 'text-brand-500' : ''}>Publish</span>
            </div>
          </div>

          {/* ── STEP 1: Basic Details ──────────────────────────────── */}
          {step === 1 && (
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-4">

              {/* Image upload area */}
              <div className="border-2 border-dashed border-[#2a2a2a] hover:border-brand-500/40 rounded-2xl p-6 text-center transition-colors cursor-pointer">
                <Upload size={24} className="text-[#555] mx-auto mb-2" />
                <p className="text-sm text-[#555]">Drop photos here or <span className="text-brand-500">browse</span></p>
                <p className="text-[11px] text-[#333] mt-1">Listings with 3+ photos get 40% more views</p>
              </div>

              {/* Title */}
              <div>
                <label className="text-[11px] font-bold text-[#555] uppercase tracking-wider block mb-1.5">Title *</label>
                <input
                  value={form.title}
                  onChange={e => update('title', e.target.value)}
                  placeholder="iPhone 14 Pro 256GB Space Black"
                  className="w-full bg-[#111] border border-[#2a2a2a] focus:border-brand-500/50 rounded-xl px-4 py-3 text-sm text-[#e8e8e8] outline-none transition-colors"
                />
              </div>

              {/* Description */}
              <div>
                <label className="text-[11px] font-bold text-[#555] uppercase tracking-wider block mb-1.5">Description *</label>
                <textarea
                  value={form.description}
                  onChange={e => update('description', e.target.value)}
                  placeholder="Describe your item — condition, specs, reason for selling..."
                  rows={4}
                  className="w-full bg-[#111] border border-[#2a2a2a] focus:border-brand-500/50 rounded-xl px-4 py-3 text-sm text-[#e8e8e8] outline-none transition-colors resize-none"
                />
              </div>

              {/* Price + Category row */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[11px] font-bold text-[#555] uppercase tracking-wider block mb-1.5">Price (USD) *</label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[#555] text-sm">$</span>
                    <input
                      type="number"
                      value={form.price}
                      onChange={e => update('price', e.target.value)}
                      placeholder="0"
                      className="w-full bg-[#111] border border-[#2a2a2a] focus:border-brand-500/50 rounded-xl pl-7 pr-4 py-3 text-sm text-[#e8e8e8] outline-none transition-colors"
                    />
                  </div>
                </div>
                <div>
                  <label className="text-[11px] font-bold text-[#555] uppercase tracking-wider block mb-1.5">Category *</label>
                  <select
                    value={form.category}
                    onChange={e => update('category', e.target.value)}
                    className="w-full bg-[#111] border border-[#2a2a2a] focus:border-brand-500/50 rounded-xl px-4 py-3 text-sm text-[#e8e8e8] outline-none transition-colors appearance-none cursor-pointer"
                  >
                    <option value="">Select...</option>
                    {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
              </div>

              {/* Condition */}
              <div>
                <label className="text-[11px] font-bold text-[#555] uppercase tracking-wider block mb-1.5">Condition</label>
                <div className="flex gap-2 flex-wrap">
                  {CONDITIONS.map(c => (
                    <button
                      key={c}
                      onClick={() => update('condition', c)}
                      className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                        form.condition === c
                          ? 'bg-brand-500 text-white'
                          : 'bg-[#111] border border-[#2a2a2a] text-[#888] hover:border-brand-500/30'
                      }`}
                    >
                      {c}
                    </button>
                  ))}
                </div>
              </div>

              {/* Location */}
              <div>
                <label className="text-[11px] font-bold text-[#555] uppercase tracking-wider block mb-1.5">Location</label>
                <input
                  value={form.location}
                  onChange={e => update('location', e.target.value)}
                  placeholder="e.g. Tampines, Singapore"
                  className="w-full bg-[#111] border border-[#2a2a2a] focus:border-brand-500/50 rounded-xl px-4 py-3 text-sm text-[#e8e8e8] outline-none transition-colors"
                />
              </div>

              {/* Duration */}
              <div>
                <label className="text-[11px] font-bold text-[#555] uppercase tracking-wider block mb-1.5">Listing Duration</label>
                <div className="grid grid-cols-3 gap-2">
                  {DURATIONS.map(d => (
                    <button
                      key={d.hours}
                      onClick={() => update('duration_hours', d.hours)}
                      className={`p-3 rounded-xl border text-center transition-all ${
                        form.duration_hours === d.hours
                          ? 'border-brand-500 bg-brand-500/10'
                          : 'border-[#2a2a2a] bg-[#111] hover:border-brand-500/30'
                      }`}
                    >
                      <p className={`text-sm font-bold ${form.duration_hours === d.hours ? 'text-brand-500' : 'text-[#e8e8e8]'}`}>{d.label}</p>
                      <p className="text-[10px] text-[#555] mt-0.5">{d.note}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* CTA */}
              <button
                onClick={handleAiOptimize}
                disabled={!canOptimize || optimizing}
                className="w-full flex items-center justify-center gap-2 bg-brand-500 hover:bg-brand-600 disabled:opacity-40 text-white font-semibold py-3.5 rounded-xl transition-colors"
              >
                {optimizing ? (
                  <>
                    <Loader size={16} className="animate-spin" />
                    AI Optimizing...
                  </>
                ) : (
                  <>
                    <Sparkles size={16} />
                    Optimize with AI
                    <ChevronRight size={16} />
                  </>
                )}
              </button>

              <button
                onClick={() => setStep(3)}
                disabled={!canOptimize}
                className="w-full text-[#555] hover:text-[#888] text-sm py-2 transition-colors"
              >
                Skip AI — publish directly
              </button>
            </motion.div>
          )}

          {/* ── STEP 2: AI Results ───────────────────────────────────── */}
          {step === 2 && aiResult && (
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-4">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles size={16} className="text-purple-400" />
                <span className="text-sm font-semibold text-purple-400">AI Analysis Complete</span>
                <span className="text-[10px] text-[#555] ml-auto">Deal score: {aiResult.deal_score}/100</span>
              </div>

              {/* Deal score bar */}
              <div className="bg-[#111] border border-[#2a2a2a] rounded-xl p-4">
                <div className="flex justify-between text-xs text-[#555] mb-2">
                  <span>Deal Score</span>
                  <span className={aiResult.deal_score >= 60 ? 'text-green-400' : 'text-amber-400'}>
                    {aiResult.deal_score}/100
                  </span>
                </div>
                <div className="h-2 bg-[#1a1a1a] rounded-full">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-brand-600 to-brand-400 transition-all duration-700"
                    style={{ width: `${aiResult.deal_score}%` }}
                  />
                </div>
              </div>

              {/* Weak points */}
              {aiResult.weak_points.length > 0 && (
                <div className="bg-amber-500/5 border border-amber-500/20 rounded-xl p-4">
                  <p className="text-[11px] font-bold text-amber-400 uppercase mb-2">⚠️ Improvements Needed</p>
                  {aiResult.weak_points.map((w, i) => (
                    <p key={i} className="text-sm text-[#a0a0a0] flex items-center gap-2">
                      <AlertTriangle size={11} className="text-amber-500 shrink-0" />
                      {w}
                    </p>
                  ))}
                </div>
              )}

              {/* AI suggestions */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <p className="text-[11px] font-bold text-[#888] uppercase tracking-wider">AI-Optimized Version</p>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <span className="text-xs text-[#555]">Use AI version</span>
                    <div
                      onClick={() => setUseAiVersion(!useAiVersion)}
                      className={`w-9 h-5 rounded-full transition-colors relative cursor-pointer ${useAiVersion ? 'bg-brand-500' : 'bg-[#2a2a2a]'}`}
                    >
                      <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-all ${useAiVersion ? 'left-4' : 'left-0.5'}`} />
                    </div>
                  </label>
                </div>

                <div className="bg-[#111] border border-[#2a2a2a] rounded-xl p-4 space-y-3">
                  <div>
                    <p className="text-[10px] text-[#555] mb-1">Title</p>
                    <p className="text-sm text-[#e8e8e8]">{aiResult.optimized_title}</p>
                  </div>
                  <div>
                    <p className="text-[10px] text-[#555] mb-1">Description</p>
                    <p className="text-xs text-[#a0a0a0] line-clamp-3">{aiResult.optimized_description}</p>
                  </div>
                  <div>
                    <p className="text-[10px] text-[#555] mb-1">Suggested Price</p>
                    <p className="price-tag text-brand-500">${aiResult.suggested_price?.toFixed(0)}</p>
                    {aiResult.suggested_price < parseFloat(form.price) && (
                      <p className="text-[10px] text-green-400 mt-0.5">↓ Reduce by ${(parseFloat(form.price) - aiResult.suggested_price).toFixed(0)} to sell faster</p>
                    )}
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {aiResult.suggested_tags?.map(tag => (
                      <span key={tag} className="bg-[#1a1a1a] text-[#888] text-[10px] px-2 py-0.5 rounded-md">{tag}</span>
                    ))}
                  </div>
                </div>
              </div>

              <button
                onClick={() => setStep(3)}
                className="w-full flex items-center justify-center gap-2 bg-brand-500 hover:bg-brand-600 text-white font-semibold py-3.5 rounded-xl transition-colors"
              >
                Review & Publish
                <ChevronRight size={16} />
              </button>
            </motion.div>
          )}

          {/* ── STEP 3: Publish ─────────────────────────────────────── */}
          {step === 3 && (
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-4">
              <div className="bg-[#111] border border-[#2a2a2a] rounded-2xl p-5 space-y-3">
                <h3 className="font-semibold text-[#e8e8e8]">Listing Preview</h3>

                <div className="bg-[#1a1a1a] rounded-xl p-3">
                  <p className="font-semibold text-sm text-[#f0f0f0]">
                    {useAiVersion && aiResult ? aiResult.optimized_title : form.title}
                  </p>
                  <p className="price-tag text-brand-500 text-xl mt-1">${form.price}</p>
                  <div className="flex gap-3 mt-2 text-[11px] text-[#555]">
                    <span>{form.location}</span>
                    <span>·</span>
                    <span>{form.condition}</span>
                    <span>·</span>
                    <span>{form.duration_hours}h duration</span>
                  </div>
                </div>

                <div className="text-xs text-[#555] space-y-1">
                  <p className="flex items-center gap-2">
                    <CheckCircle size={12} className="text-green-400" />
                    AI-powered engagement signals will activate immediately
                  </p>
                  <p className="flex items-center gap-2">
                    <CheckCircle size={12} className="text-green-400" />
                    Listing will be indexed in search within 60 seconds
                  </p>
                  <p className="flex items-center gap-2">
                    <CheckCircle size={12} className="text-green-400" />
                    Hourly price intelligence updates enabled
                  </p>
                </div>
              </div>

              <button
                onClick={handlePublish}
                disabled={submitting}
                className="w-full flex items-center justify-center gap-2 bg-brand-500 hover:bg-brand-600 disabled:opacity-50 text-white font-bold py-4 rounded-xl transition-colors text-base"
              >
                {submitting ? <Loader size={18} className="animate-spin" /> : '🚀'}
                {submitting ? 'Publishing...' : 'Publish Listing'}
              </button>

              <button
                onClick={() => setStep(step - 1)}
                className="w-full text-[#555] hover:text-[#888] text-sm py-2 transition-colors"
              >
                ← Back
              </button>
            </motion.div>
          )}
        </div>
      </div>
    </>
  )
}
