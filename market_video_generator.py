import os
import textwrap
import time
from datetime import datetime

import feedparser
import numpy as np
import requests
import yfinance as yf
from bs4 import BeautifulSoup
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont

# MoviePy import compatibility (v1/v2)
try:
    from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
    from moviepy.video.fx.all import fadein, fadeout
except Exception:  # pragma: no cover
    # MoviePy v2+ exposes classes directly under moviepy, and uses effects.
    from moviepy import AudioFileClip, ImageClip, concatenate_videoclips  # type: ignore
    from moviepy.video.fx.FadeIn import FadeIn  # type: ignore
    from moviepy.video.fx.FadeOut import FadeOut  # type: ignore

    def fadein(clip, duration):  # type: ignore
        return clip.with_effects([FadeIn(duration)])

    def fadeout(clip, duration):  # type: ignore
        return clip.with_effects([FadeOut(duration)])


def _with_duration(clip, duration_seconds):
    if hasattr(clip, "set_duration"):
        return clip.set_duration(duration_seconds)
    return clip.with_duration(duration_seconds)


def _with_audio(clip, audio_clip):
    if hasattr(clip, "set_audio"):
        return clip.set_audio(audio_clip)
    return clip.with_audio(audio_clip)


class IndianMarketVideoGenerator:
    def __init__(self):
        self.width = 1080
        self.height = 1920
        self.bg_color = (10, 25, 47)  # Dark blue
        self.accent_color = (0, 200, 83)  # Green for positive
        self.red_color = (255, 82, 82)  # Red for negative

        # FFmpeg params for maximum device compatibility:
        # - H.264 + yuv420p is the most broadly supported video combo
        # - AAC-LC stereo at 44.1kHz is widely supported
        # - faststart moves the moov atom to the beginning for better streaming
        self._ffmpeg_compat_params = [
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            "-profile:v",
            "main",
            "-level",
            "4.0",
            "-ac",
            "2",
        ]

    def fetch_market_news(self):
        """Fetch latest Indian market news"""
        news_data = []

        feeds = [
            "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
            "https://www.moneycontrol.com/rss/marketoutlook.xml",
        ]

        for feed_url in feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:3]:
                    news_data.append(
                        {
                            "title": entry.title,
                            "summary": entry.summary if hasattr(entry, "summary") else entry.title,
                            "link": entry.link,
                        }
                    )
            except Exception as e:
                print(f"Error fetching from {feed_url}: {e}")

        return news_data[:5]

    def get_market_indices(self):
        """Simulated market data fallback."""
        return {
            "NIFTY 50": {
                "value": "21,731.40",
                "change": "+145.70",
                "percent": "+0.67%",
                "trend": "up",
            },
            "SENSEX": {
                "value": "71,941.57",
                "change": "+418.60",
                "percent": "+0.58%",
                "trend": "up",
            },
            "BANK NIFTY": {
                "value": "46,235.45",
                "change": "-89.30",
                "percent": "-0.19%",
                "trend": "down",
            },
        }

    def get_real_market_indices(self):
        """Fetch real-time-ish Indian market data via yfinance."""
        indices = {
            "^NSEI": "NIFTY 50",
            "^BSESN": "SENSEX",
            "^NSEBANK": "BANK NIFTY",
        }

        market_data = {}

        for symbol, name in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="2d")

                if len(data) >= 2:
                    current = float(data["Close"].iloc[-1])
                    previous = float(data["Close"].iloc[-2])
                    change = current - previous
                    percent_change = (change / previous) * 100

                    market_data[name] = {
                        "value": f"{current:,.2f}",
                        "change": f"{'+' if change > 0 else ''}{change:,.2f}",
                        "percent": f"{'+' if percent_change > 0 else ''}{percent_change:.2f}%",
                        "trend": "up" if change > 0 else "down",
                    }
            except Exception as e:
                print(f"Error fetching {name}: {e}")

        return market_data

    def create_background(self, color):
        """Create gradient background"""
        img = Image.new("RGB", (self.width, self.height), color)
        draw = ImageDraw.Draw(img)

        for i in range(self.height):
            alpha = i / self.height
            r = int(color[0] * (1 - alpha * 0.3))
            g = int(color[1] * (1 - alpha * 0.3))
            b = int(color[2] * (1 - alpha * 0.3))
            draw.line([(0, i), (self.width, i)], fill=(r, g, b))

        return np.array(img)

    def _load_fonts(self):
        try:
            return {
                "title": ImageFont.truetype("arial.ttf", 80),
                "subtitle": ImageFont.truetype("arial.ttf", 50),
                "date": ImageFont.truetype("arial.ttf", 40),
                "header": ImageFont.truetype("arial.ttf", 60),
                "index": ImageFont.truetype("arial.ttf", 45),
                "value": ImageFont.truetype("arial.ttf", 55),
                "news_header": ImageFont.truetype("arial.ttf", 50),
                "news_title": ImageFont.truetype("arial.ttf", 55),
                "news_summary": ImageFont.truetype("arial.ttf", 40),
                "outro_title": ImageFont.truetype("arial.ttf", 70),
                "outro_subtitle": ImageFont.truetype("arial.ttf", 45),
            }
        except Exception:
            default = ImageFont.load_default()
            return {k: default for k in [
                "title",
                "subtitle",
                "date",
                "header",
                "index",
                "value",
                "news_header",
                "news_title",
                "news_summary",
                "outro_title",
                "outro_subtitle",
            ]}

    def create_title_frame(self):
        """Create opening title frame"""
        fonts = self._load_fonts()
        img = Image.fromarray(self.create_background(self.bg_color).astype("uint8"))
        draw = ImageDraw.Draw(img)

        title_text = "INDIAN MARKET"
        title_bbox = draw.textbbox((0, 0), title_text, font=fonts["title"])
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(
            ((self.width - title_width) / 2, 400),
            title_text,
            fill=self.accent_color,
            font=fonts["title"],
        )

        subtitle_text = "TODAY'S OUTLOOK"
        subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=fonts["subtitle"])
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        draw.text(
            ((self.width - subtitle_width) / 2, 520),
            subtitle_text,
            fill=(255, 255, 255),
            font=fonts["subtitle"],
        )

        date_text = datetime.now().strftime("%B %d, %Y")
        date_bbox = draw.textbbox((0, 0), date_text, font=fonts["date"])
        date_width = date_bbox[2] - date_bbox[0]
        draw.text(
            ((self.width - date_width) / 2, 1400),
            date_text,
            fill=(200, 200, 200),
            font=fonts["date"],
        )

        return np.array(img)

    def create_indices_frame(self, indices):
        """Create frame showing market indices"""
        fonts = self._load_fonts()
        img = Image.fromarray(self.create_background(self.bg_color).astype("uint8"))
        draw = ImageDraw.Draw(img)

        header = "MARKET INDICES"
        header_bbox = draw.textbbox((0, 0), header, font=fonts["header"])
        header_width = header_bbox[2] - header_bbox[0]
        draw.text(
            ((self.width - header_width) / 2, 200),
            header,
            fill=self.accent_color,
            font=fonts["header"],
        )

        y_position = 400
        for name, data in indices.items():
            color = self.accent_color if data["trend"] == "up" else self.red_color

            draw.text((100, y_position), name, fill=(255, 255, 255), font=fonts["index"])
            draw.text((100, y_position + 60), data["value"], fill=color, font=fonts["value"])

            change_text = f"{data['change']} ({data['percent']})"
            draw.text((100, y_position + 130), change_text, fill=color, font=fonts["index"])

            arrow = "▲" if data["trend"] == "up" else "▼"
            draw.text((850, y_position + 60), arrow, fill=color, font=fonts["value"])

            draw.line(
                [(100, y_position + 200), (980, y_position + 200)],
                fill=(100, 100, 100),
                width=2,
            )
            y_position += 280

        return np.array(img)

    def create_news_frame(self, news_item, index):
        """Create frame for news item"""
        fonts = self._load_fonts()
        img = Image.fromarray(self.create_background(self.bg_color).astype("uint8"))
        draw = ImageDraw.Draw(img)

        header = f"NEWS UPDATE #{index + 1}"
        draw.text((100, 200), header, fill=self.accent_color, font=fonts["news_header"])

        title = news_item["title"]
        wrapped_title = textwrap.fill(title, width=30)
        draw.text((100, 320), wrapped_title, fill=(255, 255, 255), font=fonts["news_title"])

        summary_raw = news_item.get("summary") or ""
        summary = (summary_raw[:200] + "...") if len(summary_raw) > 200 else summary_raw
        wrapped_summary = textwrap.fill(summary, width=35)
        draw.text((100, 700), wrapped_summary, fill=(200, 200, 200), font=fonts["news_summary"])

        return np.array(img)

    def create_outro_frame(self):
        """Create closing frame"""
        fonts = self._load_fonts()
        img = Image.fromarray(self.create_background(self.bg_color).astype("uint8"))
        draw = ImageDraw.Draw(img)

        main_text = "STAY INVESTED"
        main_bbox = draw.textbbox((0, 0), main_text, font=fonts["outro_title"])
        main_width = main_bbox[2] - main_bbox[0]
        draw.text(
            ((self.width - main_width) / 2, 700),
            main_text,
            fill=self.accent_color,
            font=fonts["outro_title"],
        )

        subtitle = "Follow for Daily Updates"
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=fonts["outro_subtitle"])
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        draw.text(
            ((self.width - subtitle_width) / 2, 820),
            subtitle,
            fill=(255, 255, 255),
            font=fonts["outro_subtitle"],
        )

        disclaimer = "*Not financial advice. Do your own research."
        draw.text((100, 1600), disclaimer, fill=(150, 150, 150), font=fonts["outro_subtitle"])

        return np.array(img)

    def generate_voiceover(self, text, filename):
        """Generate voiceover using gTTS"""
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(filename)
        return AudioFileClip(filename)

    def create_video(self):
        """Main function to create the video"""
        print("Fetching market data...")
        news_items = self.fetch_market_news()

        indices = self.get_real_market_indices()
        if not indices:
            print("Real index fetch returned empty; falling back to simulated data.")
            indices = self.get_market_indices()

        clips = []
        audio_clips = []

        print("Creating title frame...")
        title_frame = self.create_title_frame()
        title_clip = _with_duration(ImageClip(title_frame), 3)
        title_clip = fadeout(fadein(title_clip, 0.5), 0.5)
        clips.append(title_clip)

        print("Creating indices frame...")
        indices_frame = self.create_indices_frame(indices)
        indices_clip = _with_duration(ImageClip(indices_frame), 5)

        indices_text = "Today's market update. "
        for name, data in indices.items():
            trend = "up" if data["trend"] == "up" else "down"
            indices_text += f"{name} is at {data['value']}, {trend} by {data['percent']}. "

        indices_audio = self.generate_voiceover(indices_text, "temp_indices_audio.mp3")
        audio_clips.append(indices_audio)
        indices_clip = _with_audio(indices_clip, indices_audio)
        clips.append(indices_clip)

        print("Creating news frames...")
        for i, news in enumerate(news_items[:3]):
            news_frame = self.create_news_frame(news, i)
            news_clip = _with_duration(ImageClip(news_frame), 4)

            news_text = f"News update {i + 1}. {news['title']}"
            news_audio = self.generate_voiceover(news_text, f"temp_news_audio_{i}.mp3")
            audio_clips.append(news_audio)
            news_clip = _with_audio(news_clip, news_audio)
            clips.append(news_clip)

        print("Creating outro frame...")
        outro_frame = self.create_outro_frame()
        outro_clip = _with_duration(ImageClip(outro_frame), 3)
        outro_clip = fadeout(fadein(outro_clip, 0.5), 0.5)
        clips.append(outro_clip)

        print("Combining all clips...")
        final_video = concatenate_videoclips(clips, method="compose")

        output_filename = f"indian_market_outlook_{datetime.now().strftime('%Y%m%d')}.mp4"
        print(f"Exporting video to {output_filename}...")

        try:
            final_video.write_videofile(
                output_filename,
                fps=30,
                codec="libx264",
                audio_codec="aac",
                audio_fps=44100,
                audio_bitrate="192k",
                temp_audiofile="temp-audio.m4a",
                remove_temp=True,
                preset="medium",
                ffmpeg_params=self._ffmpeg_compat_params,
            )
        finally:
            # Ensure all file handles are released before deleting temp assets (Windows).
            for a in audio_clips:
                try:
                    a.close()
                except Exception:
                    pass
            for c in clips:
                try:
                    c.close()
                except Exception:
                    pass
            try:
                final_video.close()
            except Exception:
                pass

            print("Cleaning up temporary files...")
            temp_files = [f"temp_news_audio_{i}.mp3" for i in range(3)] + ["temp_indices_audio.mp3"]
            for path in temp_files:
                if not os.path.exists(path):
                    continue
                for _ in range(10):
                    try:
                        os.remove(path)
                        break
                    except PermissionError:
                        time.sleep(0.2)

        print(f"Video created successfully: {output_filename}")
        return output_filename


if __name__ == "__main__":
    generator = IndianMarketVideoGenerator()
    generator.create_video()
