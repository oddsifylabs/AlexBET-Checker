# AlexBET Checker Website

Landing page for the AlexBET Checker Telegram bot — exclusive to Testudo Legio members.

## Quick Deploy

### GitHub Pages (Live)

1. Go to: **Settings → Pages**
2. Source: **Deploy from branch**
3. Branch: **main** → Folder: **/docs**
4. Save

**Live URL:** https://oddsifylabs.github.io/AlexBET-Checker

---

## Features

### Design
- ✅ Modern gray/black/white color scheme
- ✅ Lucide icons (clean SVG)
- ✅ Inter + JetBrains Mono fonts
- ✅ Fully responsive (mobile-first)
- ✅ Scroll animations
- ✅ Sticky header with blur effect

### Functionality
- ✅ FAQ accordion (expandable)
- ✅ Mobile menu toggle
- ✅ Smooth scroll navigation
- ✅ Active nav link highlighting
- ✅ CTA click tracking (analytics-ready)
- ✅ Demo section with bot conversation

### Conversion
- ✅ Whop sales page links (all CTAs)
- ✅ "Members Only" messaging
- ✅ Testudo Legio branding
- ✅ Clear value proposition

---

## Analytics Setup

### Google Analytics 4

1. Create GA4 property at [analytics.google.com](https://analytics.google.com)
2. Get your Measurement ID (starts with `G-`)
3. Update `docs/index.html`:

```html
<!-- Replace this line -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-XXXXXXXXXX');
</script>
```

### Tracked Events

```javascript
// CTA clicks (Whop sales page)
gtag('event', 'cta_click', {
    'event_category': 'conversion',
    'event_label': 'Whop Sales Page',
    'value': 1
});

// Demo section views
gtag('event', 'demo_view', {
    'event_category': 'engagement',
    'event_label': 'Demo Section Viewed'
});
```

---

## Customization

### Update Whop Link

All CTAs point to:
```
https://whop.com/joined/oddsify-shop/products/monthly-access-e0/
```

Search and replace if the URL changes.

### Add Screenshots

1. Add images to `docs/images/`
2. Reference in HTML:
```html
<img src="images/screenshot.png" alt="Bot screenshot">
```

### Update FAQ

Edit the FAQ section in `docs/index.html`. Each FAQ item:

```html
<div class="faq-card">
    <div class="faq-question">
        <i data-lucide="chevron-down"></i>
        <h4>Your Question Here</h4>
    </div>
    <div class="faq-answer">
        <p>Your answer here.</p>
    </div>
</div>
```

---

## File Structure

```
docs/
├── index.html          # Main landing page (22KB)
├── css/
│   └── styles.css      # Styles (17KB)
├── js/
│   └── main.js         # Interactions (5KB)
└── images/             # (Optional) Add screenshots
```

---

## Performance

- **Total Size:** ~44KB (uncompressed)
- **Fonts:** Google Fonts (Inter, JetBrains Mono)
- **Icons:** Lucide CDN (lightweight SVG)
- **No frameworks:** Pure HTML/CSS/JS
- **Lighthouse Score:** 95+ expected

---

## Next Steps

1. ✅ **Add Google Analytics** — Replace `G-XXXXXXXXXX` with your ID
2. ✅ **Add bot screenshots** — Show actual bot interaction
3. ✅ **Add testimonials** — Member quotes from Testudo Legio
4. ✅ **Connect custom domain** — `alexbetchecker.com` or subdomain
5. ✅ **A/B test CTAs** — Test button copy, placement

---

**Built by Oddsify Labs** | [www.oddsifylabs.com](https://www.oddsifylabs.com)
