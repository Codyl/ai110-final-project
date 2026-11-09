# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

Cody's Music Recommender

---

## 2. Intended Use

It builds a short playlist of 5 songs from one user profile.

It puts mood and energy first. It assumes the user has one favorite genre and one favorite mood.
It is for classroom exploration. It is not for real users.

---

## 3. How the Model Works

Every song gets a score from 0 to 8. The score is a sum of small parts. Each part checks one thing the user told us.

- Energy: up to 2 points. The closer the song, the more points.
- Genre: 2 points if it matches exactly. Otherwise 0.
- Mood: 1 point if it matches exactly. Otherwise 0.
- Acoustic sound: up to 1 point. "Likes acoustic" aims for 0.8. Otherwise it aims for 0.2.
- Valence (how happy it sounds): up to 1 point. Closer is better.
- Danceability: up to 0.5 points. Closer is better.
- Tempo: up to 0.5 points. Closer is better.

Any preference the user skips is ignored. The top 5 songs win. A small random bonus (up to 0.3) shakes up close scores.
Each artist can show up once, so one band cannot take the whole list.

**Vibe search (optional).** A user can describe the music they want in words. Embeddings retrieve the 10 closest songs, a language model turns the request into numeric preferences, code validates them, and the same scorer ranks the 10 songs. If the model step fails, the closest matches are shown instead.

---

## 4. Data

- The catalog has 31 songs in `data/songs.csv`.
- It has 15 artists. Many are film, choir, classical, and rock acts.
- Genre labels are long and mixed, like "Celtic / Classical crossover". Most appear only once.
- Mood labels are two-word phrases, like "Sad, emotional". All 30 are different.
- The web app can add songs through a lookup API. I curated the starter songs and YouTube IDs by hand.
- Missing: jazz, R&B, lofi, country (just one song), Latin, and most hip-hop. Almost every song is English.
- Missing: lyrics, release year, and who else listened to a song.

---

## 5. Strengths

- It works well when the user copies a catalog label exactly. "Classical" plus "Melancholic, contemplative" gives Moonlight Sonata at 7.82 of 8.
- Opposite users get opposite lists. A calm acoustic listener and a loud metal fan share no songs.
- The numeric parts find sensible neighbors. A calm Classical profile also gets Amazing Grace and Hedwig's Theme. Those are quiet and acoustic too.
- Every score comes with reasons. I can see why a song ranked where it did.
- A profile with just one preference (energy only) still works.

---

## 6. Limitations and Bias

**The biggest weakness: genre and mood are exact text matches.** The catalog uses long labels like "Heavy metal / Rock" and "Magical, mysterious". A user who types "pop" or "happy" matches no song at all, and "pop" is not even equal to "Pop". So those two preferences quietly score zero for everyone, and the list falls back on the numbers. The other way around, an exact match jumps a song to the top: Moonlight Sonata scores 7.82 and the next song only 4.86. That jump creates a filter bubble. Users who spell it right see their own genre again and again. Users who spell it wrong never see their genre at all.

Other problems:

- Similar genres get no credit. "Folk rock" is not close to "Country / Folk" for this model.
- Only one favorite genre and mood are allowed. Most people like several.
- Energy, tempo, valence, and danceability move together. Together they count more than they should.
- There is no way to ask for something new. The same taste gives the same songs. Only the random bonus changes them.
- With no preferences, every song scores 0. The order then falls back to the alphabet.
- The catalog is small and Western. Fans of music that is missing get weaker results.

---

## 7. Evaluation

I ran 7 profiles with a fixed seed and no random bonus, so results repeat. Run `python scripts/run_evidence.py` to reproduce them. The full output is saved in `assets/evidence.txt`. The catalog now has 31 songs, so the numbers below come from the latest run.

**Profiles tested**

| Profile           | What it asks for                                                 |
| ----------------- | ---------------------------------------------------------------- |
| A. Pop / happy    | Starter profile. Lowercase "pop" and "happy". High energy.       |
| B. Pop / sad      | Exact labels "Pop" and "Sad, emotional". Medium energy only.     |
| C. Calm classical | "Classical", "Melancholic, contemplative". Low energy. Acoustic. |
| D. Loud metal     | "Heavy metal", "Aggressive, energetic". Very high energy.        |
| E. Energy only    | Just energy 0.9. Nothing else.                                   |
| F. Contradiction  | Classical and sad, but also very high energy and not acoustic.   |
| G. No preferences | Empty profile.                                                   |

**Top pick for each profile**

| Profile | #1 song                          | Score | #2 score |
| ------- | -------------------------------- | ----- | -------- |
| A       | Wake Me Up                       | 4.63  | 4.60     |
| B       | Apologize                        | 5.00  | 1.90     |
| C       | Moonlight Sonata                 | 5.72  | 2.95     |
| D       | Enter Sandman                    | 4.90  | 1.90     |
| E       | Believer (three-way tie at 2.00) | 2.00  | 2.00     |
| F       | Symphony No. 5                   | 4.05  | 3.10     |
| G       | A Thousand Years (all tied at 0) | 0.00  | 0.00     |

**Pair comparisons**

- **A vs B (pop/happy vs Pop/sad).** The two users sound alike, but their lists are very different. B gets a clear winner, Apologize at 5.00, then a big drop to 1.90. A's top five are bunched between 4.32 and 4.63. B typed the exact catalog text. A typed "pop" and "happy", which match nothing. The only difference is spelling, and that is unfair to A.
- **A vs D (pop/happy vs loud metal).** Believer shows up in both lists. A has no genre match, so A's list is just "high energy, upbeat, not acoustic". Without a genre match, the numbers decide, and loud songs look alike to the numbers.
- **C vs D (calm classical vs loud metal).** No songs overlap. C gets quiet, acoustic songs. D gets loud ones. This is the result I hoped for.
- **C vs F (calm classical vs contradiction).** Both want "Classical". But F also wants high energy and no acoustic sound. Moonlight Sonata drops out and Symphony No. 5 takes #1, since it is Classical and loud. Energy is worth 2 points and mood only 1, so energy wins the argument.
- **D vs E (loud metal vs energy only).** E has no genre, so Duel of the Fates (orchestral) and Battle Hymn of the Republic (choir) show up. With energy alone, any loud song counts the same.
- **E vs G (energy only vs nothing).** E gets real scores up to 2.00. G gets 0.00 for every song and falls back to the alphabet, which is a bias in itself.
- **B vs C (sad pop vs calm classical).** Each profile has one song that matches the label (5.00 and 5.72). After that, the next song scores 2.95 or lower. The rest only match by numbers.

**Guardrail experiments** (also in `assets/evidence.txt`)

| Experiment                                                  | Result                                                                  |
| ----------------------------------------------------------- | ----------------------------------------------------------------------- |
| Pass `None`, a non-dict, or a song with a blank `energy`    | Raises a clear `ValueError` or `TypeError`. It is not scored.           |
| Impossible targets (energy 50, valence -9, 5000 bpm)        | Scores stay between 0.39 and 1.16. They never go negative or past 8.    |
| Ask for 10 songs                                            | 10 songs, at most 1 per artist.                                         |
| Same seed twice                                             | Same list. Passing `previous_ids` gives a different list.               |
| `"Classical"` vs `"classical"` vs `" Classical "`           | 2.00, 0.00, 0.00. Matching is exact. This is the known weakness.        |
| Vibe search: model reply is prose, not JSON                 | Falls back to closest matches, flagged `used_fallback=True` with a note. |
| Vibe search: model names a genre not in the retrieved songs | The genre is dropped. Other valid preferences are kept.                 |
| Vibe search: empty or 301-character request                 | Rejected with a plain message before any model call.                    |

**Automated tests**

`python -m pytest` runs 128 tests. **125 pass and 3 fail.** I left the failures in and did not hide them:

- Two starter tests in `test_recommender.py` build a `UserProfile` with 4 fields. It now needs 7. The tests are out of date.
- `test_edge_profile_loud_cased_genre_and_mood_still_match` expects "LoFi" and " Chill " to match. The scoring code does not lowercase or trim. This one is a real weakness, not a stale test.

The 23 vibe-search tests use a fake Bedrock client. They prove the retrieval, validation, caching, fallback, and prompt-injection handling work as coded. They do not prove that a real model writes good preferences. The evidence file shows the vibe pipeline with a stub, not a live AWS run.

**What surprised me**

- A single capital letter matters more than any number. "pop" scored nothing, and "Pop" scored 3 more points than a near miss.
- Every profile with a label match (B, C, D) has a big gap between #1 and #2. One lucky label match beats four good numeric matches.
- The old README sample showed "genre matches pop". That came from an older catalog. With today's songs, the starter profile never gets a genre match.
- The web app avoids the spelling problem by using dropdowns built from the catalog's labels. The CLI and the tests do not have that protection.

---

## 8. Future Work

- Make genre and mood matching forgiving. Lowercase and trim the text first.
- Split labels like "K-pop / Hip-hop" into parts. Give partial credit for each shared part.
- Use one short mood list ("sad", "happy", "calm") instead of free-form phrases.
- Let users list several favorite genres and moods.
- Add an "explore" switch that rewards songs unlike the user's usual picks.
- Add more songs, and more kinds of music.
- Lower the weight of features that move together, like energy and tempo.
- Make a no-preference profile return random songs, not alphabetical ones.
- Explain results in plain words, like "This is quiet like Moonlight Sonata".

---

## 9. Personal Reflection

- I learned that a recommender is just a score and a sort. The choices behind the score matter most.
- What surprised me most was how small input details change the whole result. One capital letter flipped a score from 0 to 8.
- A filter bubble does not need a fancy model. A big bonus for an exact match is enough to make users see the same thing again.
- I used to think a bad result meant a bad song list. Now I think it often means a bad label, or a bad weight.
- Next time I want to try this: ask what the user would want to hear that they did not ask for.
- When I use Spotify or YouTube now, I want to ask what they reward, and what they never show me.

---

## 10. AI Collaboration

I built this with Claude Code, and used it for code, tests, and documentation.

**One suggestion that helped.** The AI proposed scoring in small, optional parts, where a preference the user skips is simply ignored. It also suggested normalizing tempo to a 0-1 range so BPM could not swamp the other terms. That made the scorer easy to test one part at a time. It is why single-preference and no-preference profiles work. The same idea shaped vibe search: the model only suggests numbers, and the existing scorer stays in charge of ranking.

**One suggestion that was flawed.** The AI's first README sample and starter profile assumed labels like "pop" and "happy" would match. They match nothing in the real catalog, where labels look like "EDM / Folk pop". The sample looked fine but was stale. I only caught it by running the real profiles. The run command was also wrong: `python -m src.main` fails with an import error, and `python src/main.py` works.

**How I checked AI work.** I ran the code and read the output instead of trusting the summary. I wrote edge-case tests for contradictions and impossible targets. I regenerate every number in the docs with `scripts/run_evidence.py`. For vibe search I used a fake Bedrock client in tests, so I could check the guardrails without AWS.

**What I'd tell a teammate.** Ask the AI for a way to reproduce its claim, not just the claim.

---

## 11. Biases and Testing Summary

- **Where bias shows up:** exact-text genre and mood matching, a small Western and English-heavy catalog, one favorite genre and mood only, and correlated features counted several times. With vibe search there is one more: the embedding and chat models were trained on data I cannot inspect, so their idea of "calm" or "sad" may not match every listener's.
- **Who it hurts:** users who spell a label differently, and fans of music the catalog lacks. A big bonus for an exact match also creates a filter bubble.
- **Misuse and safety:** vibe search takes free text, so a user could try to inject instructions. The request is wrapped as data, the reply is clamped and filtered, and the model cannot add songs that were not retrieved. Input is capped at 300 characters. The song-lookup API key and AWS credentials stay server-side.
- **What testing showed:** 125 of 128 tests pass. Guardrails hold (bad input rejected, scores bounded, one song per artist, bad model replies fall back safely). The 3 failures are 2 stale tests and 1 real weakness (case and spacing in labels).
- **What I have not tested:** a live Bedrock run, and how good the model's preferences are across many different requests.
- **What I would fix first:** lowercase and trim labels, then split labels like "K-pop / Hip-hop" into parts for partial credit.
