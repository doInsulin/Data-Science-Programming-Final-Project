import streamlit as st

st.set_page_config(page_title="Predictions Report", layout="wide")
st.title("Prediction")

md = """
# Hit Analysis – Predicting Hit Anime Series in January 2026

This module uses cleaned AniList data from 2016–2025 to construct a regression model with "whether it's a sequel, average popularity of the production company, production format, number of episodes, duration, average rating, and genre-specific popularity vector" as the main features. A Random Forest Regressor is used, and GridSearchCV is employed for hyperparameter search on the R² metric (50% CV). Finally, the model is trained on all training data and used to predict anime series for the winter of 2026. The results are written to a CSV file and ranked by popularity.

Below are some key components and data analysis methods of this module.

## Feature Engineering

**Studio Popularity Feature Values**

```python
studio_popularity = {}
for _, row in train_df.iterrows():
    studio = row.get('mainstudio', '')
    if pd.notna(studio) and studio:
        popularity = row.get('popularity', 0)
        if pd.notna(popularity):
            studio_popularity[studio] = studio_popularity.get(studio, []) + [popularity]

for studio in studio_popularity:
    studio_popularity[studio] = np.mean(studio_popularity[studio])
```

- **studio_popularity**: Stores a list of popularity values for each studio using a dictionary.
- **Data Collection**:
  - Extract studio names (`mainstudio` field)

  - Extract the popularity value for the anime (`popularity` field)

  - Add the popularity value to the corresponding studio's list

- **Data Cleaning**:
  - `pd.notna(studio)`: Ensures the studio name is not empty

  - `and studio`: Ensures the studio name is not an empty string

  - `pd.notna(popularity)`: Ensures the popularity value is not empty

- **Average Calculation**:
  - Calculate the average popularity for each studio using `np.mean()`

  - Result: Dictionary `studio_popularity[studio] = average popularity`


**Theme Encoding**

```python
# Create a genre type encoder
all_genres = set()
for genre_str in train_df['genres']:
    genres = extract_genres(genre_str)
    all_genres.update(genres)

genre_encoder = {genre: i for i, genre in enumerate(sorted(all_genres))}
```

Process the raw format within the loop, return the list of themes, and add the theme of the current work to the overall collection.

Create an encoder that assigns a unique index to each theme (result: `genre_encoder = {'Action': 0, 'Adventure': 1, ...}`).

**Feature Extraction**

```python
for _, row in test_df.iterrows():
    test_ids.append(row.get('id', ''))
    test_titles.append(row.get('title', ''))
    
    features = []
    
    # 1. Whether it is a sequel
    features.append(is_sequel(row.get('title', '')))
```

Feature: Continuation judgment (binary feature)

- **Call**: `is_sequel(row.get('title_romaji', ''))`

- **Return**: 0 or 1

```python
    studio = row.get('studio', '') or row.get('studio_list', '')
    features.append(get_studio_popularity(studio, studio_popularity))

    format_type = str(row.get('format', 'TV')).strip()
    format_map = {'TV': 1, 'MOVIE': 2, 'OVA': 3, 'ONA': 4, 'SPECIAL': 5}
    features.append(format_map.get(format_type, 0))

    episodes = row.get('episodes', 0)
    features.append(episodes if pd.notna(episodes) else 0)

    duration = row.get('duration', 0)
    features.append(duration if pd.notna(duration) else 0)

    avg_score = row.get('averagescore', 0)
    features.append(avg_score if pd.notna(avg_score) else 0)
```

Features: Studio popularity, release method, number of episodes, runtime, rating.

- Studio Popularity: Well-known studios typically produce high-quality works.

- Release Method: Reflects the release method and production scale of the work.

- Number of Episodes: Reflects the length and investment of the work.

- Runtime: Length of each episode.

- Rating: A quality indicator of the work.

**Genre One-Hot Code**

```python
genre_vector = [0] * len(genre_encoder)
genres = extract_genres(row.get('genres', ''))
for genre in genres:
    if genre in genre_encoder:
        genre_vector[genre_encoder[genre]] = 1

features.extend(genre_vector)
```

**Processing Method**:

1. **Initialize Vector**: Create a vector filled with zeros, with a length equal to the total number of theme types.
   - For example: If there are 50 different theme types, create a zero vector of length 50.


2. **Extract Themes**: Call the `extract_genres()` function to return a list of themes for the current work.


3. **Set Flags**:

   - Iterate through each theme of the current work.


   - Find the corresponding index position in `genre_encoder`.


   - Set the value at that position to 1.


4. Add the one-hot encoding to the feature column using `features.extend(genre_vector)`.

## Results

### Top10 Predicted Popularity

| Rank | Title                                    | Predicted Popularity |
| ---- | ---------------------------------------- | -------------------- |
| 1    | Fate/strange Fake                        | 50273.4              |
| 2    | Jigokuraku 2nd Season                    | 34273.2              |
| 3    | Eris no Seihai                           | 28170.6              |
| 4    | Mato Seihei no Slave 2                   | 24646.7              |
| 5    | Jingai Kyoushitsu no Ningengirai Kyoushi | 23794.1              |
| 6    | Okiraku Ryoushu no Tanoshii Ryouchi Boue | 22871.4              |
| 7    | Jujutsu Kaisen: Shimetsu Kaiyuu - Zenpen | 22677.5              |
| 8    | [Oshi no Ko] 3rd Season                  | 22236.5              |
| 9    | Sousou no Frieren 2nd Season             | 19472.2              |
| 10   | 29-sai Dokushin Chuuken Boukensha no Nic | 18883.4              |

### Studio Average Predicted Popularity Ranking

*(Studios with ≥1 Anime)*

| Rank | Studio           | Avg Predicted Popularity | Count |
| ---- | ---------------- | ------------------------ | ----- |
| 1    | MAPPA            | 28475.3                  | 2     |
| 2    | Ashi Productions | 28170.6                  | 1     |
| 3    | A-1 Pictures     | 25453.8                  | 2     |
| 4    | Hayabusa Film    | 24646.7                  | 1     |
| 5    | Passione         | 24646.7                  | 1     |
| 6    | Asread           | 23794.1                  | 1     |
| 7    | NAZ              | 22871.4                  | 1     |
| 8    | Doga Kobo        | 22236.5                  | 1     |
| 9    | MADHOUSE         | 19472.2                  | 1     |
| 10   | HORNETS          | 18883.4                  | 1     |
| 11   | A.C.G.T.         | 18802.1                  | 1     |
| 12   | David Production | 16847.9                  | 1     |
| 13   | J.C.STAFF        | 13380.5                  | 1     |
| 14   | 8-bit            | 12468.8                  | 1     |
| 15   | Signal.MD        | 12453.6                  | 1     |

## Model Performance Summary

**Model Type:** Random Forest Regressor (Grid Search Optimized)

**Best Parameters:**  

```json
{
    "bootstrap": true,
    "max_depth": 20,
    "max_features": "sqrt",
    "min_samples_leaf": 1,
    "min_samples_split": 2,
    "n_estimators": 200
}
```

**Training R² Score:** 0.9290

**Validation R² Score:** 0.5465

Key patterns observed in the results:

- **Signature Effect:** Sequels and existing IPs (such as Sousou no Frieren, Jigokuraku, and the Fate series) received higher predicted values, indicating that historical popularity in the training set has a strong predictive power for subsequent works of the same IP.

- **Large Studio Effect:** The high average popularity of studios like MAPPA, A-1 Pictures, and MADHOUSE in the training set was used as a "studio_popularity" feature, tending to boost the predicted value of new anime from those studios.

- **Genre Preference:** Action/fantasy/supernatural genres frequently appeared on the high-popularity list, and the training set statistics showed that the unique popularity vectors of these genres had a positive impact on the model.

- **Long Tail and Uncertainty:** A small number of smaller studios or new works also received moderate predicted values in the rankings, showing that the model did not rely solely on "head" features.

Considering the current industry environment, we found that the predicted results mostly favored existing IPs and sequels. This is because sequels come with a built-in user base and promotional budget, and streaming platforms tend to prioritize purchasing or promoting large IPs, thereby amplifying their popularity in the short term.

The current model can capture key signals such as "IP effect, production company, and genre," providing reasonable Top-N predictions, which is valuable for content planning and distribution prioritization. However, if used as a basis for decision-making, it should be supplemented with more preceding and market signals, report uncertainties, and adopt logarithmic targets and richer model integration strategies to reduce bias and improve the ability to identify sudden hits.
"""

st.markdown(md)
