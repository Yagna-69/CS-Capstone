# Wishlist Feature - Implementation Notes

## Current Implementation (Client-Side)

The wishlist feature is currently implemented using **localStorage** for persistence. This means:
- Wishlist data is stored locally in the browser
- Data persists across browser sessions
- Data is tied to the specific browser/device
- No server-side persistence or synchronization across devices

### Storage Details
- **Key**: `fxtrade_wishlist`
- **Format**: JSON array of `{ pair: string, addedAt: timestamp }`
- **Location**: Browser localStorage

## Future Database Implementation

When ready to add server-side persistence, implement:

### 1. Database Schema
```sql
CREATE TABLE wishlist (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    pair VARCHAR(10) NOT NULL,
    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, pair)
);

CREATE INDEX idx_wishlist_user_id ON wishlist(user_id);
```

### 2. Backend API Endpoints
Add to `backend/routes/portfolio.py`:
- `GET /api/portfolio/wishlist` - Fetch user's wishlist
- `POST /api/portfolio/wishlist` - Add pair to wishlist
- `DELETE /api/portfolio/wishlist` - Remove pair from wishlist

### 3. Frontend Integration
Update `frontend/src/stores/portfolio.js`:
- Replace localStorage methods with API calls
- Add `fetchWishlist()` method
- Implement optimistic updates with rollback on error
- Add to `portfolioApi` in `services/api.js`

### 4. Migration Path
When implementing database persistence:
1. Create migration to add wishlist table
2. Optionally migrate existing localStorage data on first login
3. Update store methods to use API instead of localStorage
4. Remove localStorage fallback
