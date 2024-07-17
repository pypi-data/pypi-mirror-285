NSFW pipeline that classifies prompt, using a bi-lstm model

| Feature | Description |
| --- | --- |
| **Name** | `en_prompt_nsfw_pipeline_bilstm` |
| **Version** | `0.1.1` |
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
| **`textcat`** | `underage_safe`, `adult`, `cp`, `safe` |

</details>

### Accuracy

| Type | Score |
| --- | --- |
| `CATS_SCORE` | 90.56 |
| `CATS_MICRO_P` | 90.63 |
| `CATS_MICRO_R` | 90.63 |
| `CATS_MICRO_F` | 90.63 |
| `CATS_MACRO_P` | 90.67 |
| `CATS_MACRO_R` | 90.51 |
| `CATS_MACRO_F` | 90.56 |
| `CATS_MACRO_AUC` | 98.71 |
| `TOK2VEC_LOSS` | 260845.08 |
| `TEXTCAT_LOSS` | 835.83 |