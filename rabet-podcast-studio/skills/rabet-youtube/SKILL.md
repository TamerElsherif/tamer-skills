---
name: rabet-youtube
description: Write YouTube metadata for Rabet (رابط) Podcast full episodes and mini episodes — 3–5 title options paired with thumbnails, a humanized Egyptian-Arabic description with guest/host LinkedIn links, timestamped chapters from the transcript (shifted for a teaser), channel call to action, hashtags and a tags field. Use when the user asks for titles, a description, chapters, timestamps, hashtags or tags for an episode upload. Part of the rabet-podcast-studio set.
---

# Rabet YouTube metadata

Output: `Ep<N>_YouTube_Title_Description.txt` next to the thumbnails (mini episodes: one file listing every sub-episode).

## Titles
3–5 options, each < 100 characters, each paired with a thumbnail, ending `| رابط بودكاست - الحلقة N`
(mini episodes: `| رابط بودكاست - الحلقة N`, with the topic first). A question or tension, B2B, insightful;
no clickbait claim the episode doesn't make; no title starts with an English word. Recommend one.

## Description (Egyptian Arabic + English terms; run it through the **humanizer** skill)
1. Two-sentence hook naming the tension, then who talks about what.
2. Guests and host: `name | title`, LinkedIn link on the next line. Ask for any link you don't have.
   Rabet: https://www.youtube.com/@RabetPodcast · https://www.linkedin.com/company/rabet-podcast
   Tamer: https://www.linkedin.com/in/tamer-elsherif-it-ai · Hossam: https://www.linkedin.com/in/hossam-ezzat ·
   Haitham: https://www.linkedin.com/in/haitham-fouad/ (prodXeed: https://www.linkedin.com/company/prodxeed)
3. «محاور الحلقة:» chapters: first line `00:00`, ascending, ≥ 10 s apart, 15–35 for a full episode.
4. Subscribe call to action + channel link, LinkedIn page, ~12 hashtags (#رابط_بودكاست #بودكاست_تقني
   #الذكاء_الاصطناعي #RabetPodcast + topic tags), then a comma tags list (< 500 characters).
5. A NOTES block for the user: which file the chapters match, what to change if a different file is uploaded.

## Chapters that are actually right
- Transcribe **the file being uploaded** (or prep the master and add the offset). Old transcripts may be offset by a
  teaser (EP1: +34 s; Ep 3: +58 s) — compare first lines and ffprobe both files before reusing any times.
- A chapter time = the start of the line where the topic starts (the host's question, if there is one).
- Mini episodes: use the section starts from the build (`<spec>.render.json` / the .docx brief), not the master times.
- Verify lengths in a script: titles < 100, tags < 500, description < 5000 characters.

## Uploading (Postiz → Rabet YouTube, integration `yt_brand` in `~/.rabet-reels.json`)
- Video files are almost always > 100 MB: use rabet-social's temporary-URL route (size check, tell the user,
  `tunnel_upload.py`, close it after). Never post a big file to the Postiz upload API (HTTP 413).
- Post settings: `title`, `type` **private** (the user makes it public), `selfDeclaredMadeForKids` no, `thumbnail`
  {id, path}, `tags` [{value, label}]. Description = the post content, one `<p>` per line.
- Videos over 15 min need a verified channel; custom thumbnails too.

## Playlists, category, language
Every upload goes into its playlist (names in `~/.rabet-reels.json` → `youtube.playlists`):

| Video | Playlist |
|---|---|
| Full episode | **Full Episodes** |
| Mini / sub / topic episode | **Mini Episodes - Topics** |
| Reel / Short | none unless the user names one |

Category **Science & Technology** (`28`), language **Arabic**, made for kids **no**.
- **Postiz** has no playlist, category or language field (checked 2026-11-01). After the upload, give the user one
  checklist per video: Studio → video → Details → Playlists / Show more → Category, Language.
- **Zernio** sets them at upload time when the Rabet YouTube channel is connected there: `platformSpecificData`
  `playlistId`, `categoryId: "28"`, `visibility: "private"`, `madeForKids: false`, `firstComment` (optional).
  Find the playlist id by its **exact** title on that account (`youtube-playlists`); if it's missing, ask before
  creating it (create as private). Never create a second playlist with the same name.
  Prefer Zernio for YouTube once it's connected: it also takes full episodes (Postiz's URL upload stops at ~1 GB),
  with `validate_media` first.
- Report per video which playlist it went into, or that it still needs to be added by hand.
