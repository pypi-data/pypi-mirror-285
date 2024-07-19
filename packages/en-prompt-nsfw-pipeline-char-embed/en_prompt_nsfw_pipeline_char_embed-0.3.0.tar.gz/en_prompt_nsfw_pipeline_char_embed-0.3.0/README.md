NSFW pipeline that classifies prompt, using a character embedding model

| Feature | Description |
| --- | --- |
| **Name** | `en_prompt_nsfw_pipeline_char_embed` |
| **Version** | `0.3.0` |
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
| **`textcat`** | `safe`, `cp`, `underage_safe`, `adult` |

</details>

### Accuracy

| Type | Score |
| --- | --- |
| `CATS_SCORE` | 88.96 |
| `CATS_MICRO_P` | 90.14 |
| `CATS_MICRO_R` | 90.14 |
| `CATS_MICRO_F` | 90.14 |
| `CATS_MACRO_P` | 90.68 |
| `CATS_MACRO_R` | 87.93 |
| `CATS_MACRO_F` | 88.96 |
| `CATS_MACRO_AUC` | 98.29 |
| `TOK2VEC_LOSS` | 7740.17 |
| `TEXTCAT_LOSS` | 819.21 |