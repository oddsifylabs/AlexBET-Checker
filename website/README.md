# AlexBET Checker Website

Landing page for the AlexBET Checker Telegram bot.

## Quick Deploy

### Option 1: GitHub Pages (Free)

1. Push this repo to GitHub
2. Go to Settings → Pages
3. Source: Deploy from branch → `main` → `/website` folder
4. Your site will be live at: `https://oddsifylabs.github.io/AlexBET-Checker`

### Option 2: Vercel (Free)

1. Push to GitHub
2. Import project on [Vercel](https://vercel.com)
3. Set root directory to `website`
4. Deploy!

### Option 3: Netlify (Free)

1. Push to GitHub
2. Connect repo on [Netlify](https://netlify.com)
3. Set publish directory to `website`
4. Deploy!

### Option 4: Custom Domain

Deploy to any static hosting (Vercel, Netlify, Cloudflare Pages) and connect your domain:
- `alexbetchecker.com`
- `checker.oddsifylabs.com`
- `alexbet.io`

## File Structure

```
website/
├── index.html      # Main landing page
├── css/
│   └── styles.css  # Dark theme, responsive styles
├── js/
│   └── main.js     # Scroll animations, CTA tracking
└── images/         # (Optional) Add screenshots, logos
```

## Customization

### Update Bot Link

Replace all instances of `https://t.me/AlexBETCheckerBot` with your actual bot username.

### Add Analytics

In `js/main.js`, add your analytics tracking:

```javascript
// Google Analytics
gtag('event', 'cta_click', {
    'event_category': 'engagement',
    'event_label': 'Add to Telegram'
});
```

### Add Screenshots

1. Add images to `website/images/`
2. Reference in HTML: `<img src="images/screenshot.png" alt="Bot screenshot">`

## Features

- ✅ Dark theme (matches Oddsify Labs branding)
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Scroll animations
- ✅ Clear CTAs to Telegram bot
- ✅ Roadmap section (shows future features)
- ✅ Examples section (shows input formats)
- ✅ SEO meta tags

## Next Steps

1. **Add bot screenshots** — Show the bot in action
2. **Add testimonials** — User quotes from Testudo Legio
3. **Add FAQ section** — Common questions about the bot
4. **Add analytics** — Track CTA clicks and conversions
5. **Connect domain** — Professional URL for marketing

---

**Built by Oddsify Labs** | [www.oddsifylabs.com](https://www.oddsifylabs.com)
