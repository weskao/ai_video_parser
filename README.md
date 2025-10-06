# YouTube Shorts HTML Parser

A Python script to parse YouTube Shorts HTML files and generate a summary report.

## Features

- Extract Shorts **titles**, **hashtags**, and **view counts**.
- Compute total videos, total views, average views.
- Identify highest and lowest viewed videos.
- Top 10 keywords and hashtags.
- View count distribution: 0-10k / 10k-100k / 100k-1M / 1M-10M / 10M+.
- Sort videos by views.
- Save results to `result` folder and open in VS Code.

## Setup

1. Ensure Python ≥ 3.7 is installed:

    ```python
    python --version
    ```

2. Place your YouTube HTML files in the `html` folder:

    ```text
    project/
    ├─ html/
    │  ├─ example1.html
    │  ├─ example2.html
    ├─ parse_yt_shorts_html.py
    ```

## Usage

Run the script:

```bash
python parse_yt_shorts_html.py
```

- Scans all `.html` files in `html`.
- Parses video info.
- Saves output to `result/result_CHANNELNAME.txt`.
- Opens output in VS Code if available.

## Output Format

```text
1.
Video Title
#hashtag1 #hashtag2
Views: 1234

===== SUMMARY =====
Total videos: 50
Total views: 1234567
Average views: 24691
Highest views video: Example Video (Views: 50000)
Lowest views video: Example Video 2 (Views: 100)

===== TOP KEYWORDS =====
keyword1 (12)
keyword2 (9)

===== TOP HASHTAGS =====
#tag1 (15)
#tag2 (10)

===== VIEWS DISTRIBUTION =====
10M+: 0 videos
1M-10M: 2 videos
100k-1M: 10 videos
10k-100k: 25 videos
0-10k: 13 videos

```

## Configuration

```python
HTML_FOLDER = "html"
OUTPUT_FOLDER = "result"

STOPWORDS = set([
    "the", "a", "an", "and", "or", "in", "on", "for", "to", "with",
    "of", "is", "it", "this", "that", "as", "at", "by", "from",
    "you", "your", "i", "we", "my", "me", "our", "be", "are"
])

```

- Change folders or stopwords as needed.

## Notes

- Titles "Home" or empty strings are ignored.
- Supports old and new YouTube HTML formats.
- Parses Chinese view numbers (萬, 億).
- If VS Code is unavailable, results are still saved to `result` folder.
