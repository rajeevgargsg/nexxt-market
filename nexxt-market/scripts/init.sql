-- NexxtMarket Database Initialization
-- Run automatically on first Docker Compose boot

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- for full-text search

-- Categories seed data
INSERT INTO categories (id, name, slug, icon) VALUES
  (uuid_generate_v4(), 'Electronics', 'electronics', '📱'),
  (uuid_generate_v4(), 'Vehicles', 'vehicles', '🚗'),
  (uuid_generate_v4(), 'Furniture', 'furniture', '🛋️'),
  (uuid_generate_v4(), 'Fashion', 'fashion', '👗'),
  (uuid_generate_v4(), 'Sports', 'sports', '⚽'),
  (uuid_generate_v4(), 'Books', 'books', '📚'),
  (uuid_generate_v4(), 'Property', 'property', '🏠'),
  (uuid_generate_v4(), 'Other', 'other', '📦')
ON CONFLICT DO NOTHING;

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_listings_status ON listings(status);
CREATE INDEX IF NOT EXISTS idx_listings_category ON listings(category_id);
CREATE INDEX IF NOT EXISTS idx_listings_expires ON listings(expires_at);
CREATE INDEX IF NOT EXISTS idx_listings_rank ON listings(rank_score DESC);
CREATE INDEX IF NOT EXISTS idx_listings_seller ON listings(seller_id);
CREATE INDEX IF NOT EXISTS idx_messages_listing ON messages(listing_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, is_read);
CREATE INDEX IF NOT EXISTS idx_saved_user ON saved_listings(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_listing ON listing_activity_logs(listing_id, created_at);
