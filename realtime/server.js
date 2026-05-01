/**
 * NexxtMarket Real-time Server
 * Pushes live signals, activity events to connected browsers via WebSocket
 */
const express = require('express')
const http = require('http')
const { Server } = require('socket.io')
const { createClient } = require('redis')

const app = express()
const server = http.createServer(app)

const io = new Server(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST'],
  },
})

// ─── Redis Pub/Sub ────────────────────────────────────────────────────────────
const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379'

const subscriber = createClient({ url: REDIS_URL })
const publisher = createClient({ url: REDIS_URL })

subscriber.on('error', err => console.error('Redis subscriber error:', err))
publisher.on('error', err => console.error('Redis publisher error:', err))

async function startRedis() {
  await subscriber.connect()
  await publisher.connect()

  // Subscribe to engagement events published by backend scheduler
  await subscriber.subscribe('listing:signals', (message) => {
    try {
      const data = JSON.parse(message)
      const { listing_id, signals } = data
      // Push to all users viewing this listing
      io.to(`listing:${listing_id}`).emit('signals_updated', signals)
      // Push to feed viewers
      io.to('feed').emit('listing_activity', { listing_id, signals })
    } catch (err) {
      console.error('Failed to process message:', err)
    }
  })

  await subscriber.subscribe('listing:activity', (message) => {
    try {
      const data = JSON.parse(message)
      // Broadcast activity (views, saves, messages) to listing room
      io.to(`listing:${data.listing_id}`).emit('activity', data)
    } catch (err) {}
  })

  await subscriber.subscribe('notifications', (message) => {
    try {
      const data = JSON.parse(message)
      // Send to specific user room
      io.to(`user:${data.user_id}`).emit('notification', data)
    } catch (err) {}
  })

  console.log('Redis subscriptions active')
}

// ─── Socket.IO ────────────────────────────────────────────────────────────────
io.on('connection', (socket) => {
  console.log(`Client connected: ${socket.id}`)

  // Join listing room to receive real-time signals
  socket.on('join:listing', (listingId) => {
    socket.join(`listing:${listingId}`)
    console.log(`${socket.id} joined listing:${listingId}`)
  })

  // Join feed room
  socket.on('join:feed', () => {
    socket.join('feed')
  })

  // Join user notification room
  socket.on('join:user', (userId) => {
    socket.join(`user:${userId}`)
  })

  socket.on('leave:listing', (listingId) => {
    socket.leave(`listing:${listingId}`)
  })

  socket.on('disconnect', () => {
    console.log(`Client disconnected: ${socket.id}`)
  })
})

// ─── Health check ─────────────────────────────────────────────────────────────
app.get('/health', (_, res) => res.json({ status: 'ok', connections: io.engine.clientsCount }))

// ─── Start ────────────────────────────────────────────────────────────────────
const PORT = process.env.PORT || 3001

server.listen(PORT, () => {
  console.log(`⚡ NexxtMarket Real-time server running on port ${PORT}`)
  startRedis().catch(err => {
    console.warn('Redis not available — running without pub/sub:', err.message)
  })
})
