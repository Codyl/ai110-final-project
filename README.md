# 🎵 Music Recommender

A music recommender with a command-line runner and a Streamlit web app. Give it a taste profile (genre, mood, energy, and so on), or just describe a vibe in plain words, and it returns a short playlist with a reason for every pick.

## Base project

This extends my **Music Recommender Simulation** from Modules 1-3. That project had a catalog (`data/songs.csv`), a `Song` and `UserProfile` model, and a basic scoring rule. For the final project I turned it into a fuller system:

- Split the code into small modules (loading, scoring, ranking, player, song API client, vibe search).
- Added a Streamlit app with preference controls, search, an "All songs" table, and embedded YouTube players.
- Added **vibe search**, a retrieval-augmented (RAG) step: you describe the music you want, embeddings retrieve candidate songs, an LLM turns the request into numeric preferences, and the original scorer ranks the result.
- Added a song-lookup client that can pull audio features for a new track and add it to the catalog.
- Added ranking guardrails (artist diversity, no repeated lists, bounded scores) and a large test suite.
- Grew the catalog to 31 real songs with YouTube IDs.

## How it works

There are two ways in. Both end at the same scorer.

```
Preferences (sliders / dict) ─────────────────────────┐
                                                      ▼
"calm music for studying" → embed → retrieve top 10 → LLM → validate → score_song → rank → playlist
                            (Titan)  (cosine sim)     (Claude) (guardrails)  (same scorer)
```

1. **Load.** `song_loader.py` reads `data/songs.csv`. Each song has genre, mood, energy, valence, danceability, acousticness, tempo, and a YouTube ID.
2. **Score.** `scoring.py` gives each song 0 to 8 points by adding up how well it fits each preference you gave. Preferences you skip are ignored.

   | Part         | Max points | Rule                                    |
   | ------------ | ---------- | --------------------------------------- |
   | Energy       | 2.0        | closer to your target is better         |
   | Genre        | 2.0        | exact text match, otherwise 0           |
   | Mood         | 1.0        | exact text match, otherwise 0           |
   | Acousticness | 1.0        | "likes acoustic" aims for 0.8, else 0.2 |
   | Valence      | 1.0        | closer is better                        |
   | Danceability | 0.5        | closer is better                        |
   | Tempo        | 0.5        | normalized 60-180 bpm, closer is better |

3. **Rank.** `ranking.py` adds a small random bonus (up to 0.3) so near-ties can swap, allows one song per artist, and can avoid repeating the previous list. The score returned is the real one, without the bonus.
4. **Explain.** Every result carries the reasons behind its score, shown in the app under "Why this recommendation?".

### Vibe search (RAG)

`src/vibe_search.py` adds an AI front end:

1. **Retrieve.** Each song is turned into a short sentence ("low energy, calm; dark, sad-sounding; slow tempo...") and embedded with Amazon Titan on AWS Bedrock. Your request is embedded the same way, and the 10 closest songs are retrieved by cosine similarity. Embeddings are cached in `data/embeddings_cache.json`.
2. **Generate.** Claude reads your request and only those 10 songs, then replies with numeric preferences as JSON.
3. **Validate.** The JSON is checked before use: numbers are clamped to valid ranges, unknown keys are dropped, and a genre must exactly match one of the retrieved songs. The model never picks songs itself.
4. **Rank.** The existing scorer ranks the retrieved songs with those preferences.
5. **Fall back.** If Bedrock fails or the reply is unusable, you get the closest matches by similarity, flagged `used_fallback=True` with a note saying why.

Files: `src/main.py` (CLI), `src/app.py` (Streamlit), `src/recommender.py` (`Recommender` class over the same functions), `src/player.py` (YouTube embeds), `src/song_api.py` (song lookup), `src/vibe_search.py` (RAG).

## Why you can trust it

The core is a transparent rule-based scorer, not a black box, so any result can be checked by hand. The AI step only suggests numbers, and everything it says is checked before it is used.

- **Explainable.** Each score is a sum of listed parts, and the reasons are shown with each song.
- **Bounded.** Scores cannot go negative or above 8, even for impossible targets.
- **Validated input.** Missing or malformed data raises a clear error instead of being scored. Vibe requests must be 1-300 characters.
- **AI is boxed in.** The model's reply is clamped, filtered, and limited to retrieved songs. Text in your request is wrapped as data, and an injected "return song 999" cannot add a song.
- **Fails safe.** If the AI step breaks, the app still returns a playlist and says so.
- **Diverse.** One artist cannot fill the list.
- **Tested.** 128 automated tests run in under a second, using a fake Bedrock client, so no AWS calls or cost. 125 pass and 3 fail; see [Testing results](#testing-results) for why.
- **Honest about limits.** Genre and mood are exact text matches (see [Limitations](#limitations-and-risks) and the [model card](model_card.md)). The web app uses dropdowns built from the catalog's own labels, so users cannot mistype them there.

## Getting started

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Mac or Linux
pip install -r requirements.txt
```

Run the command-line demo from the repo root:

```bash
python src/main.py
```

Run the web app:

```bash
streamlit run src/app.py
```

Optional setup:

- Adding new songs from the app needs an `API_KEY` in a `.env` file.
- Vibe search needs AWS credentials with Bedrock access. Set `AWS_REGION` and, if needed, `BEDROCK_LLM_MODEL_ID` (the chat model must be enabled in your account). Everything else works without AWS.

Run the tests and regenerate the evidence file:

```bash
python -m pytest
python scripts/run_evidence.py
```

## Example inputs and outputs

Examples 1-3 come from `python scripts/run_evidence.py` (seed 0, random bonus off, so they repeat exactly). The full run is in [assets/evidence.txt](assets/evidence.txt).

**1. A user who types exact catalog labels (Pop / Sad, emotional, medium energy)**

```
prefs: {'favorite_genre': 'Pop', 'favorite_mood': 'Sad, emotional', 'target_energy': 0.5}
1. Apologize - OneRepublic [Pop] score 5.00
   because: energy 0.50 vs target 0.50 (+2.00 of 2.00); genre matches Pop (+2.00); mood matches Sad, emotional (+1.00)
2. Experience - Ludovico Einaudi [Contemporary classical] score 1.90
3. Nothing Else Matters - Metallica [Heavy metal / Rock] score 1.90
4. Take Me Home, Country Roads - John Denver [Country / Folk] score 1.90
5. You Raise Me Up - Celtic Woman [Celtic / Classical crossover] score 1.90
```

**2. The starter profile (lowercase "pop" and "happy")**

```
prefs: {'favorite_genre': 'pop', 'favorite_mood': 'happy', 'target_energy': 0.8, 'likes_acoustic': False, 'target_valence': 0.8, 'target_danceability': 0.8, 'target_bpm': 120.0}
1. Wake Me Up - Avicii [EDM / Folk pop] score 4.63
   because: energy 0.85 vs target 0.80 (+1.90 of 2.00); genre EDM / Folk pop is not pop (+0.00); mood Uplifting, adventurous is not happy (+0.00); acousticness 0.15 vs target 0.20 (+0.95 of 1.00); valence 0.65 vs target 0.80 (+0.85 of 1.00); danceability 0.70 vs target 0.80 (+0.45 of 0.50); tempo 124 bpm vs target 120 bpm (+0.48 of 0.50)
2. I Lived - OneRepublic [Pop rock] score 4.60
3. Dynamite - BTS [K-pop / Disco pop] score 4.51
4. Believer - Imagine Dragons [Alternative rock] score 4.40
5. CASTLE OF GLASS - Linkin Park [Alternative] score 4.32
```

No song gets a genre or mood match here, because catalog labels are long ("EDM / Folk pop"). The list falls back on the numbers.

**3. A calm, acoustic classical listener**

```
prefs: {'favorite_genre': 'Classical', 'favorite_mood': 'Melancholic, contemplative', 'target_energy': 0.2, 'likes_acoustic': True}
1. Moonlight Sonata - Beethoven [Classical] score 5.72
   because: energy 0.25 vs target 0.20 (+1.90 of 2.00); genre matches Classical (+2.00); mood matches Melancholic, contemplative (+1.00); acousticness 0.98 vs target 0.80 (+0.82 of 1.00)
2. The Sound of Silence - Simon & Garfunkel [Folk rock] score 2.95
3. A Thousand Years - Christina Perri [Pop / Acoustic] score 2.80
4. Amazing Grace - Celtic Woman [Traditional / Choral] score 2.80
5. Come Thou Fount of Every Blessing - Tabernacle Choir [Sacred choral] score 2.60
```

**4. Vibe search, with a stubbed model (no AWS call)**

The retrieval, validation, and ranking code are the real code. The embeddings and the model reply are stand-ins, so the evidence repeats without credentials. The list is ordered with the small random bonus, so scores can look slightly out of order.

```
summary: Quiet, sad, acoustic.
preferences kept: {'target_energy': 0.2, 'target_valence': 0.3, 'likes_acoustic': True}
(favorite_genre 'Rock' was not an exact genre in the retrieved songs, so the guardrail dropped it)
1. A Thousand Years - Christina Perri score 3.75
2. Amazing Grace - Celtic Woman score 3.60
3. The Sound of Silence - Simon & Garfunkel score 3.75
4. Moonlight Sonata - Beethoven score 3.52
5. Hedwig's Theme - John Williams score 3.60
```

**5. Guardrails**

```
None prefs: ValueError: user_prefs and song must not be None
song missing 'energy': ValueError: song is missing values for: energy
Impossible targets: min score 0.39, max score 1.16 (never outside 0 to 8)
k=10 results: 10 songs, most songs by one artist: 1

used_fallback=True
note: Showing the closest matches by similarity because the AI step failed: model reply contained no JSON object

''...: Describe the vibe you want first, for example: calm music for studying.
'xxxxxxxxxx'...: Keep the description under 300 characters (it is 301).

favorite_genre='Classical' -> 2.00 | 'classical' -> 0.00 | ' Classical ' -> 0.00
```

## Testing results

`python -m pytest` runs 128 tests: **125 pass, 3 fail.** The failures are known:

| Failing test                                                                  | Why                                                                                                                  |
| ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `test_recommender.py::test_recommend_returns_songs_sorted_by_score`           | Starter test builds `UserProfile` with 4 fields; it now needs 7. The test is out of date.                            |
| `test_recommender.py::test_explain_recommendation_returns_non_empty_string`   | Same cause.                                                                                                          |
| `test_score_song.py::test_edge_profile_loud_cased_genre_and_mood_still_match` | Expects "LoFi" and " Chill " to match. Matching is exact today, so this is a real weakness, not a stale test.        |

Seven structured profiles and all guardrail runs are written up in [model_card.md](model_card.md) and reproduced in [assets/evidence.txt](assets/evidence.txt). The vibe-search tests use a fake client, so they prove the pipeline and guardrails but not the quality of real model replies. I have not recorded a live Bedrock run in the evidence.

## Limitations and risks

- Genre and mood are exact, case-sensitive text matches, so near-misses score zero.
- Only one favorite genre and mood are allowed.
- Energy, tempo, valence, and danceability move together, so they count more than they should.
- The catalog is small (31 songs), mostly English and Western, and has no lyrics.
- Vibe search can only pick from the 10 retrieved songs, so a bad retrieval limits the result.
- There is no "explore" mode, so the same taste gives the same songs.
- With no preferences, every score is 0 and the list is alphabetical.

## Reflection

The full write-up is in [model_card.md](model_card.md).

A recommender is a score and a sort, so the choices behind the score matter most. One capital letter swung a song from 0 to a high score, and a big reward for exact matches builds a filter bubble without any fancy model. Adding an LLM did not remove that problem. It moved the risk to the edges, so I kept the model on a short leash: it suggests numbers, code validates them, and the same transparent scorer makes the final call. Bias shows up in what the catalog contains, which labels count as a match, and which features get the most weight.
