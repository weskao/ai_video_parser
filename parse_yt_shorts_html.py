import re
import subprocess
from collections import Counter
import os

HTML_FILE = "info.html"
STOPWORDS = set([
    "the", "a", "an", "and", "or", "in", "on", "for", "to", "with",
    "of", "is", "it", "this", "that", "as", "at", "by", "from",
    "you", "your", "i", "we", "my", "me", "our", "be", "are"
])

def read_html(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def extract_channel_name(html: str) -> str:
    match = re.search(r'"originalUrl":"https://www\.youtube\.com/(@[^"/]+)', html)
    return match.group(1) if match else "UnknownChannel"

def extract_entity_accessibility_texts(html: str) -> list[str]:
    pattern = r'"entityId":"[^"]+","accessibilityText":"(.*?)"'
    return re.findall(pattern, html)

def parse_views(views_text: str) -> int:
    if not views_text:
        return 0
    number_str = views_text.replace("觀看次數：", "").replace("次", "").replace(",", "")
    multiplier = 1
    if "萬" in number_str:
        multiplier = 10_000
        number_str = number_str.replace("萬", "")
    elif "億" in number_str:
        multiplier = 100_000_000
        number_str = number_str.replace("億", "")
    try:
        return int(float(number_str) * multiplier)
    except ValueError:
        return 0

# ------------------- Helper Functions -------------------

def parse_line(line: str):
    """Extract title, hashtags, views_text, and views_number from one line."""
    first_hashtag_index = line.find("#")
    if first_hashtag_index != -1:
        title = line[:first_hashtag_index].strip().rstrip(",-")
        comma_index = line.find(",", first_hashtag_index)
        hashtags = line[first_hashtag_index:comma_index].strip() if comma_index != -1 else line[first_hashtag_index:].strip()
    else:
        title = line.strip()
        hashtags = ""

    views_match = re.search(r"(觀看次數：[\d\.萬億,]+次)", line)
    views_text = views_match.group(1) if views_match else ""
    views_number = parse_views(views_text)

    return title, hashtags, views_text, views_number

def extract_keywords(title: str) -> list[str]:
    words = re.findall(r"\b\w+\b", title.lower())
    return [w for w in words if w not in STOPWORDS]

def extract_hashtags(hashtags_str: str) -> list[str]:
    return re.findall(r"#\w+", hashtags_str)

def compute_views_distribution(processed: list[dict]) -> dict:
    ranges = {"0-10k":0, "10k-100k":0, "100k-1M":0, "1M-10M":0, "10M+":0}
    for item in processed:
        v = item["views_number"]
        if v < 10_000:
            ranges["0-10k"] += 1
        elif v < 100_000:
            ranges["10k-100k"] += 1
        elif v < 1_000_000:
            ranges["100k-1M"] += 1
        elif v < 10_000_000:
            ranges["1M-10M"] += 1
        else:
            ranges["10M+"] += 1
    return ranges

def write_output(file_path: str, processed: list[dict], keyword_counter: Counter, hashtag_counter: Counter, ranges: dict):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        # Write video list
        for i, item in enumerate(processed, 1):
            f.write(f"{i}.\n{item['title']}\n{item['hashtags']}\n{item['views_text']}\n\n")

        # Write summary
        total_videos = len(processed)
        total_views = sum(item["views_number"] for item in processed)
        avg_views = total_views // total_videos if total_videos > 0 else 0
        max_views_item = processed[0] if total_videos > 0 else None
        min_views_item = processed[-1] if total_videos > 0 else None

        f.write("===== SUMMARY =====\n")
        f.write(f"Total videos: {total_videos}\n")
        f.write(f"Total views: {total_views}\n")
        f.write(f"Average views: {avg_views}\n")
        if max_views_item:
            f.write(f"Highest views video: {max_views_item['title']} ({max_views_item['views_text']})\n")
        if min_views_item:
            f.write(f"Lowest views video: {min_views_item['title']} ({min_views_item['views_text']})\n")

        f.write("\n===== TOP KEYWORDS =====\n")
        for word, count in keyword_counter.most_common(10):
            f.write(f"{word} ({count})\n")

        f.write("\n===== TOP HASHTAGS =====\n")
        for tag, count in hashtag_counter.most_common(10):
            f.write(f"{tag} ({count})\n")

        f.write("\n===== VIEWS DISTRIBUTION =====\n")
        for k, v in reversed(ranges.items()):
            f.write(f"{k}: {v} videos\n")

# ------------------- Main Function -------------------

def save_results(file_path: str, results: list[str]):
    processed = []
    all_keywords = []
    all_hashtags = []

    for line in results:
        title, hashtags, views_text, views_number = parse_line(line)
        processed.append({
            "title": title,
            "hashtags": hashtags,
            "views_text": views_text,
            "views_number": views_number
        })
        all_keywords.extend(extract_keywords(title))
        all_hashtags.extend(extract_hashtags(hashtags))

    processed.sort(key=lambda x: x["views_number"], reverse=True)

    keyword_counter = Counter(all_keywords)
    hashtag_counter = Counter(all_hashtags)
    ranges = compute_views_distribution(processed)

    write_output(file_path, processed, keyword_counter, hashtag_counter, ranges)

# ------------------- Utility -------------------

def open_in_vscode(file_path: str):
    try:
        subprocess.run(["code", file_path], check=True)
    except FileNotFoundError:
        print("❌ VS Code not found, please ensure 'code' command works")

def main():
    html_content = read_html(HTML_FILE)
    channel_name = extract_channel_name(html_content)
    texts = extract_entity_accessibility_texts(html_content)

    output_folder = "result"
    file_name = os.path.join(output_folder, f"result_{channel_name}.txt")

    save_results(file_name, texts)
    print(f"✅ Parsing completed, output saved to {file_name}")
    open_in_vscode(file_name)

if __name__ == "__main__":
    main()
