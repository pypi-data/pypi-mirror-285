NSFW pipeline that classifies prompt, using a bag-of-words model

| Feature | Description |
| --- | --- |
| **Name** | `en_prompt_nsfw_pipeline_bow` |
| **Version** | `0.2.0` |
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
| **`textcat`** | `safe`, `underage_safe`, `adult`, `cp` |

</details>

### Accuracy

| Type | Score |
| --- | --- |
| `CATS_SCORE` | 88.53 |
| `CATS_MICRO_P` | 89.10 |
| `CATS_MICRO_R` | 89.10 |
| `CATS_MICRO_F` | 89.10 |
| `CATS_MACRO_P` | 88.99 |
| `CATS_MACRO_R` | 88.19 |
| `CATS_MACRO_F` | 88.53 |
| `CATS_MACRO_AUC` | 97.50 |
| `TEXTCAT_LOSS` | 399.18 |