# YouTube Channel Analyzer

Analyzes YouTube channels against 2026 best practices and generates actionable recommendations.

## Usage

```bash
node youtube-analyzer.js <channel-url>
```

Example:
```bash
node youtube-analyzer.js https://youtube.com/@learnwithadamtv
```

## Output

- **analyzer.html** - Visual dashboard with analysis and recommendations
- Console output with progress and summary

## Features

### Analysis Categories

1. **Content Strategy**
   - Long-form vs Shorts mix
   - Educational value assessment
   - Trending topic coverage
   - Niche consistency

2. **Thumbnail Effectiveness**
   - Contrast and design
   - Focal point clarity
   - Text readability
   - Branding consistency

3. **Engagement Optimization**
   - Call-to-action placement
   - Community tab usage
   - Comment response rate
   - Trending audio usage

4. **SEO Optimization**
   - Title optimization
   - Description quality
   - Tag relevance
   - Keyword usage

5. **Posting Consistency**
   - Upload schedule regularity
   - Optimal timing
   - Frequency assessment

## Best Practices Database

Includes 2026 YouTube best practices:
- 70B Shorts views daily
- 10-20ms thumbnail decision time
- 3-5x boost from trending audio
- Optimal posting times and frequency

## Report Output

The HTML report includes:
- Score cards for each category
- Checklist of best practices
- Prioritized recommendations
- Action items with expected impact

## Integration

To add YouTube Data API integration:
1. Get API key from Google Cloud Console
2. Add to .env file: `YOUTUBE_API_KEY=your-key`
3. Uncomment API calls in analyzer code

## Dependencies

- Node.js 14+
- No external npm packages (vanilla JS)
