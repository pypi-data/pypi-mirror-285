NSFW pipeline that classifies prompt, using a character embedding model

| Feature | Description |
| --- | --- |
| **Name** | `en_prompt_nsfw_pipeline_char_embed` |
| **Version** | `0.1.0` |
| **spaCy** | `>=2.0.0,<3.0.0` |
| **Default Pipeline** | `textcat` |
| **Components** | `textcat` |
| **Vectors** | 0 keys, 0 unique vectors (0 dimensions) |
| **Sources** | n/a |
| **License** | `UNLICENSED` |
| **Author** | [Jiayu Liu]() |

### Label Scheme

<details>

<summary>View label scheme (4 labels for 1 components)</summary>

| Component | Labels |
| --- | --- |
| **`textcat`** | `adult`, `cp`, `underage_safe`, `safe` |

</details>

### Accuracy

| Type | Score |
| --- | --- |
| `CATS_SCORE` | 88.95 |
| `CATS_MICRO_P` | 89.02 |
| `CATS_MICRO_R` | 89.02 |
| `CATS_MICRO_F` | 89.02 |
| `CATS_MACRO_P` | 89.27 |
| `CATS_MACRO_R` | 88.75 |
| `CATS_MACRO_F` | 88.95 |
| `CATS_MACRO_AUC` | 97.80 |
| `TEXTCAT_LOSS` | 686.95 |