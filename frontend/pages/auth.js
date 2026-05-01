import { useState } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import { motion, AnimatePresence } from 'framer-motion'
import { Eye, EyeOff, Zap, ArrowRight, User, Mail, Lock } from 'lucide-react'
import { api } from '../lib/api'
import toast from 'react-hot-toast'

export default function AuthPage() {
  const router = useRouter()
  const [mode, setMode] = useState('login') // 'login' | 'register'
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({ username: '', email: '', password: '', full_name: '' })

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      if (mode === 'register') {
        await api.post('/auth/register', {
          username: form.username,
          email: form.email,
          password: form.password,
          full_name: form.full_name,
        })
        toast.success('Account created! Sign in now.')
        setMode('login')
      } else {
        const params = new URLSearchParams()
        params.append('username', form.email)
        params.append('password', form.password)
        const res = await api.post('/auth/token', params, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        })
        localStorage.setItem('token', res.data.access_token)
        localStorage.setItem('user', JSON.stringify(res.data.user || {}))
        toast.success('Welcome back!')
        router.push('/')
      }
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Head>
        <title>{mode === 'login' ? 'Sign In' : 'Join'} — NexxtMarket</title>
      </Head>

      <div className="min-h-screen bg-[#080808] flex">
        {/* Left panel – brand */}
        <div className="hidden lg:flex flex-col justify-between w-1/2 p-16 bg-[#0d0d0d] border-r border-white/5">
          <div className="flex items-center gap-2">
            <Zap className="text-orange-500" size={28} />
            <span className="font-bebas text-3xl tracking-widest text-white">NEXXTMARKET</span>
          </div>

          <div>
            <h2 className="font-bebas text-7xl text-white leading-none mb-6">
              WHERE<br />
              <span className="text-orange-500">DEALS</span><br />
              HAPPEN<br />
              FAST.
            </h2>
            <p className="text-white/40 font-dm text-lg max-w-sm">
              Real-time price signals. Live competition data. Every listing evolves by the hour.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-4">
            {[
              { label: 'Avg. sell time', value: '4.2h' },
              { label: 'Active buyers', value: '12K+' },
              { label: 'Daily listings', value: '3.8K' },
            ].map((s) => (
              <div key={s.label} className="bg-white/5 rounded-xl p-4">
                <div className="font-bebas text-3xl text-orange-500">{s.value}</div>
                <div className="text-white/40 text-xs font-dm mt-1">{s.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Right panel – form */}
        <div className="flex-1 flex items-center justify-center p-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full max-w-md"
          >
            {/* Mobile logo */}
            <div className="flex items-center gap-2 mb-10 lg:hidden">
              <Zap className="text-orange-500" size={22} />
              <span className="font-bebas text-2xl tracking-widest text-white">NEXXTMARKET</span>
            </div>

            {/* Tab toggle */}
            <div className="flex bg-white/5 rounded-xl p-1 mb-8">
              {['login', 'register'].map((m) => (
                <button
                  key={m}
                  onClick={() => setMode(m)}
                  className={`flex-1 py-2.5 rounded-lg font-dm text-sm font-medium transition-all ${
                    mode === m
                      ? 'bg-orange-500 text-black'
                      : 'text-white/50 hover:text-white'
                  }`}
                >
                  {m === 'login' ? 'Sign In' : 'Create Account'}
                </button>
              ))}
            </div>

            <AnimatePresence mode="wait">
              <motion.form
                key={mode}
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.2 }}
                onSubmit={handleSubmit}
                className="space-y-4"
              >
                {mode === 'register' && (
                  <Field
                    icon={<User size={16} />}
                    label="Full Name"
                    name="full_name"
                    value={form.full_name}
                    onChange={handleChange}
                    placeholder="Jane Smith"
                  />
                )}
                {mode === 'register' && (
                  <Field
                    icon={<User size={16} />}
                    label="Username"
                    name="username"
                    value={form.username}
                    onChange={handleChange}
                    placeholder="janesmith"
                  />
                )}
                <Field
                  icon={<Mail size={16} />}
                  label="Email"
                  name="email"
                  type="email"
                  value={form.email}
                  onChange={handleChange}
                  placeholder="jane@email.com"
                />
                <div className="relative">
                  <Field
                    icon={<Lock size={16} />}
                    label="Password"
                    name="password"
                    type={showPw ? 'text' : 'password'}
                    value={form.password}
                    onChange={handleChange}
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPw(!showPw)}
                    className="absolute right-4 top-[38px] text-white/30 hover:text-white/70"
                  >
                    {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full mt-2 flex items-center justify-center gap-2 bg-orange-500 hover:bg-orange-400 disabled:opacity-50 text-black font-dm font-bold py-3.5 rounded-xl transition-all"
                >
                  {loading ? (
                    <div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                  ) : (
                    <>
                      {mode === 'login' ? 'Sign In' : 'Create Account'}
                      <ArrowRight size={16} />
                    </>
                  )}
                </button>
              </motion.form>
            </AnimatePresence>

            {/* Demo creds */}
            <div className="mt-6 p-4 bg-white/5 rounded-xl border border-white/10">
              <p className="text-white/40 text-xs font-dm mb-1">🧪 Demo credentials</p>
              <p className="text-white/70 text-xs font-mono">alice@demo.com / demo1234</p>
            </div>
          </motion.div>
        </div>
      </div>
    </>
  )
}

function Field({ icon, label, name, type = 'text', value, onChange, placeholder }) {
  return (
    <div>
      <label className="block text-white/50 text-xs font-dm mb-1.5">{label}</label>
      <div className="relative">
        <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-white/30">{icon}</span>
        <input
          name={name}
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          required
          className="w-full bg-white/5 border border-white/10 text-white font-dm text-sm rounded-xl pl-10 pr-4 py-3 focus:outline-none focus:border-orange-500/50 placeholder:text-white/20 transition-colors"
        />
      </div>
    </div>
  )
}
