/**
 * Composable for fetching Reddit data directly from the frontend
 * Bypasses backend to avoid GCP IP blocking issues
 */

export async function fetchWallstreetbetsPosts(limit = 12) {
  const fetchLimit = limit + 5 // Fetch extra to account for filtered posts
  const url = `https://www.reddit.com/r/wallstreetbets/hot.json?limit=${fetchLimit}`
  
  try {
    const response = await fetch(url, {
      headers: {
        'Accept': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`Reddit API returned ${response.status}`)
    }
    
    const payload = await response.json()
    const children = payload?.data?.children || []
    
    const posts = []
    for (const item of children) {
      const post = item?.data || {}
      
      // Skip stickied/pinned posts
      if (post.stickied) continue
      
      // Extract thumbnail
      let thumbnail = null
      const previewImages = post.preview?.images || []
      if (previewImages.length > 0) {
        const source = previewImages[0].source
        thumbnail = source?.url?.replace(/&amp;/g, '&') || null
      }
      
      // Fallback to thumbnail field
      if (!thumbnail) {
        const thumbUrl = post.thumbnail || ''
        if (!['self', 'default', 'nsfw', 'spoiler', ''].includes(thumbUrl)) {
          thumbnail = thumbUrl
        }
      }
      
      // Calculate relative time
      const created = post.created_utc || 0
      const now = Date.now() / 1000
      const hoursAgo = Math.floor((now - created) / 3600)
      const timeStr = hoursAgo < 24 
        ? `${hoursAgo}h ago` 
        : `${Math.floor(hoursAgo / 24)}d ago`
      
      posts.push({
        id: post.id,
        title: post.title || 'Untitled',
        author: post.author || 'Unknown',
        score: post.score || 0,
        num_comments: post.num_comments || 0,
        time: timeStr,
        url: `https://www.reddit.com${post.permalink || ''}`,
        thumbnail: thumbnail,
        flair: post.link_flair_text || '',
        selftext: post.selftext ? post.selftext.substring(0, 200) + '...' : ''
      })
      
      if (posts.length >= limit) break
    }
    
    return posts
  } catch (error) {
    console.error('Failed to fetch WSB posts:', error)
    throw error
  }
}
