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

---

## 4. Data

- The catalog has 30 songs in `data/songs.csv`.
- It has 15 artists. Many are film, choir, classical, and rock acts.
- Genre labels are long and mixed, like "Celtic / Classical crossover". Most appear only once.
- Mood labels are two-word phrases, like "Sad, emotional". All 30 are different.
- I did not add or remove songs.
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

I ran 7 profiles. I used a fixed seed and no random bonus, so results were repeatable. I also ran the tests. 75 pass and 3 fail (see below).

**Profiles tested**

| Profile           | What it asks for                                                 |
| ----------------- | ---------------------------------------------------------------- |
| A. Pop / happy    | Starter profile. Lowercase "pop" and "happy". High energy.       |
| B. Pop / sad      | Exact labels "Pop" and "Sad, emotional". Medium energy.          |
| C. Calm classical | "Classical", "Melancholic, contemplative". Low energy. Acoustic. |
| D. Loud metal     | "Heavy metal", "Aggressive, energetic". Very high energy.        |
| E. Energy only    | Just energy 0.9. Nothing else.                                   |
| F. Contradiction  | Classical and sad, but also very high energy and not acoustic.   |
| G. No preferences | Empty profile.                                                   |

**Top pick for each profile**

| Profile | #1 song                          | Score |
| ------- | -------------------------------- | ----- |
| A       | Wake Me Up                       | 4.63  |
| B       | Apologize                        | 8.00  |
| C       | Moonlight Sonata                 | 7.82  |
| D       | Enter Sandman                    | 7.48  |
| E       | Believer (three-way tie at 2.00) | 2.00  |
| F       | Symphony No. 5                   | 4.05  |
| G       | A Thousand Years (all tied at 0) | 0.00  |

**Pair comparisons**

- **A vs B (pop/happy vs Pop/sad).** The two users sound alike, but their lists are very different. B gets a perfect 8.00 with Apologize. A's best score is only 4.63. This makes sense once you see the labels. B typed the exact catalog text. A typed "pop" and "happy", which match nothing. The only difference is spelling, and that is unfair to A.
- **A vs D (pop/happy vs loud metal).** Three songs overlap: Wake Me Up, Believer, and Viva La Vida. A has no genre match, so A's list is just "high energy, upbeat, not acoustic". D's list is almost the same, plus Enter Sandman on top. That makes sense. Without a genre match, the numbers decide. Loud songs look alike to the numbers.
- **C vs D (calm classical vs loud metal).** No songs overlap at all. C gets quiet, acoustic songs. D gets loud, electric songs. This is the result I hoped for. Energy and acoustic taste pull in opposite directions.
- **C vs F (calm classical vs contradiction).** Both want "Classical". But F also wants high energy and no acoustic sound. Moonlight Sonata drops out. Symphony No. 5 takes #1, since it is Classical and loud. Apologize rises to #2 on the "sad" mood. This makes sense. Energy is worth 2 points and mood only 1, so energy wins the argument.
- **D vs E (loud metal vs energy only).** E has no genre, so Duel of the Fates (orchestral) and Battle Hymn of the Republic (choir) show up. D's list is all rock and pop. This makes sense. With energy alone, any loud song counts the same.
- **E vs G (energy only vs nothing).** E gets real scores up to 2.00. G gets 0.00 for every song. This makes sense. No preferences means nothing to measure. The alphabet breaks the tie, which is a bias in itself.
- **B vs C (sad pop vs calm classical).** Both get a near-perfect #1 (8.00 and 7.82). After that, the next song scores only 4.9 or lower. This makes sense. Each profile has one song that matches the label. The rest only match by numbers.

**What surprised me**

- A single capital letter matters more than any number. "pop" scored nothing. "Pop" scored a perfect 8.
- The README sample shows "genre matches pop". That output is from an older catalog. With today's songs, the starter profile never gets a genre match.
- Every profile with a label match (B, C, D) has a big gap between #1 and #2. One lucky label match beats four good numeric matches.
- A test called `test_edge_profile_loud_cased_genre_and_mood_still_match` fails. It expects "LoFi" and " Chill " to match. The scoring code does not lowercase or trim, so they do not. This is the same weakness as above.
- Two starter tests in `test_recommender.py` also fail. They build a `UserProfile` with only four fields, but it now needs seven.

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
