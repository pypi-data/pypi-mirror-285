NSFW pipeline that classifies prompt, using a character embedding model

| Feature | Description |
| --- | --- |
| **Name** | `en_prompt_nsfw_pipeline_char_embed` |
| **Version** | `0.1.2` |
| **spaCy** | `>=3.0.0,<4.0.0` |
| **Default Pipeline** | `tok2vec`, `textcat` |
| **Components** | `tok2vec`, `textcat` |
| **Vectors** | 514157 keys, 20000 unique vectors (300 dimensions) |
| **Sources** | n/a |
| **License** | `UNLICENSED` |
| **Author** | [Jiayu Liu]() |

### Label Scheme

<details>

<summary>View label scheme (4 labels for 1 components)</summary>

| Component | Labels |
| --- | --- |
| **`textcat`** | `cp`, `adult`, `underage_safe`, `safe` |

</details>

### Accuracy

| Type | Score |
| --- | --- |
| `CATS_SCORE` | 91.32 |
| `CATS_MICRO_P` | 91.32 |
| `CATS_MICRO_R` | 91.32 |
| `CATS_MICRO_F` | 91.32 |
| `CATS_MACRO_P` | 91.37 |
| `CATS_MACRO_R` | 91.31 |
| `CATS_MACRO_F` | 91.32 |
| `CATS_MACRO_AUC` | 98.93 |
| `TOK2VEC_LOSS` | 27145.38 |
| `TEXTCAT_LOSS` | 693.56 |