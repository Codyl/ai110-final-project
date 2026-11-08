# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

You can include a simple diagram or bullet list if helpful.

Songs use energy, mood, genre, valence, acounsticness, danceability, tempo_bpm
UserProfile stores hardcoded favorite_genre, favorite_mood, target_energy, likes_acoustic.

Real world reccomendations tend to use several systems for different contexts and goals a user might have: exploration, new user, similar users like x song, handling new songs, etc.

The version here however will only have a light content-based filtering for ease of testing.

The scoring has different weights depending on the value each metric has when selecting a song. Potential biases:

- If someone is looking specifically for any danceable song the weights will not account for that
- If genre or mood is similar but not the same it is not adding to the score, nor does it accept more than one favorite
- If a user wants to explore a direction different than their existing preferences there is no switch for that. It will only suggest the same things every time until the preferences change with a bit of variation.
- Genre outweighs the numeric fit. Genre plus mood is 3.0 of 8.0 points.
- Correlated features count several times.Energy, tempo, valence and danceability tend to move together.
- Top-5 could be mostly one artist.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

   ```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
Top recommendations:

Sunrise City - Score: 7.89
Because: energy 0.82 vs target 0.80 (+1.96 of 2.00); genre matches pop (+2.00); mood matches happy (+1.00); acousticness 0.18 vs target 0.20 (+0.98 of 1.00); valence 0.84 vs target 0.80 (+0.96 of 1.00); danceability 0.79 vs target 0.80 (+0.49 of 0.50); tempo 118 bpm vs target 120 bpm (+0.49 of 0.50)

Gym Hero - Score: 6.47
Because: energy 0.93 vs target 0.80 (+1.74 of 2.00); genre matches pop (+2.00); mood intense is not happy (+0.00); acousticness 0.05 vs target 0.20 (+0.85 of 1.00); valence 0.77 vs target 0.80 (+0.97 of 1.00); danceability 0.88 vs target 0.80 (+0.46 of 0.50); tempo 132 bpm vs target 120 bpm (+0.45 of 0.50)

Rooftop Lights - Score: 5.73
Because: energy 0.76 vs target 0.80 (+1.92 of 2.00); genre indie pop is not pop (+0.00); mood matches happy (+1.00); acousticness 0.35 vs target 0.20 (+0.85 of 1.00); valence 0.81 vs target 0.80 (+0.99 of 1.00); danceability 0.82 vs target 0.80 (+0.49 of 0.50); tempo 124 bpm vs target 120 bpm (+0.48 of 0.50)

Fiesta Eléctrica - Score: 4.52
Because: energy 0.86 vs target 0.80 (+1.88 of 2.00); genre reggaeton is not pop (+0.00); mood energetic is not happy (+0.00); acousticness 0.09 vs target 0.20 (+0.89 of 1.00); valence 0.89 vs target 0.80 (+0.91 of 1.00); danceability 0.92 vs target 0.80 (+0.44 of 0.50); tempo 96 bpm vs target 120 bpm (+0.40 of 0.50)

Concrete Kings - Score: 4.56
Because: energy 0.78 vs target 0.80 (+1.96 of 2.00); genre hip hop is not pop (+0.00); mood confident is not happy (+0.00); acousticness 0.12 vs target 0.20 (+0.92 of 1.00); valence 0.62 vs target 0.80 (+0.82 of 1.00); danceability 0.85 vs target 0.80 (+0.48 of 0.50); tempo 92 bpm vs target 120 bpm (+0.38 of 0.50)
```

**Screenshot or video** _(optional)_: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this
