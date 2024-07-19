NSFW pipeline that classifies prompt, using a bag-of-words model

| Feature | Description |
| --- | --- |
| **Name** | `en_prompt_nsfw_pipeline_bow` |
| **Version** | `0.3.0` |
| **spaCy** | `>=3.0.0,<4.0.0` |
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
| **`textcat`** | `safe`, `cp`, `underage_safe`, `adult` |

</details>

### Accuracy

| Type | Score |
| --- | --- |
| `CATS_SCORE` | 89.45 |
| `CATS_MICRO_P` | 90.45 |
| `CATS_MICRO_R` | 90.45 |
| `CATS_MICRO_F` | 90.45 |
| `CATS_MACRO_P` | 90.27 |
| `CATS_MACRO_R` | 88.71 |
| `CATS_MACRO_F` | 89.45 |
| `CATS_MACRO_AUC` | 97.92 |
| `TEXTCAT_LOSS` | 347.75 |