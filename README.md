# Multi-output_Learning
# 🤖 NTHU NLP Homework 3 – Multi-Output BERT Model

This project is part of the **Natural Language Processing course** at National Tsing Hua University, implemented by [Yu-Hsuan Li (李宥萱)](https://github.com/your-github-username).

I explore **multi-output learning using BERT** on a semantic similarity and classification task. The project compares a joint multi-task model against separate task-specific models, including performance evaluations and hyperparameter tuning.


---

## 🚀 Environment

- **Platform**: Google Colab  
- **Python Version**: Colab default (3.x)  
- **GPU**: T4

---

## 📚 Model Choice

We use the [**google-bert/bert-base-uncased**](https://huggingface.co/google-bert/bert-base-uncased) model from Hugging Face.  
**Why?**  
- It is a well-established, general-purpose BERT model.
- Suitable for both regression and classification.
- Provides a strong baseline for multi-task NLP.

---

## 📈 Results

### Multi-output (Joint) Model
- Spearman Correlation: **0.8208**
- Accuracy: **0.8707**
- F1 Score: **0.8651**
<img width="1072" height="533" alt="image" src="https://github.com/user-attachments/assets/a32a8298-e148-416a-af7e-ccdcffaff8b4" />


### Separate Models (Regression + Classification)
- Spearman Correlation: **0.8201**
- Accuracy: **0.8486**
- F1 Score: **0.8473**

**Conclusion**: The multi-output model performed slightly better, likely due to shared semantic knowledge between tasks, enhancing generalization.

---

## 🔍 Error Analysis

- **Semantic complexity**: Difficult samples with ambiguous or subtle meanings.
- **Label imbalance**: The model may overfit to dominant classes.
- **Sequence length**: BERT truncates input >512 tokens, losing context.
- **Data noise**: Informal text, typos, or abbreviations reduce robustness.

---

## 🧪 Improvements Tested

### 🔁 Epochs
| Epochs | Spearman | Accuracy | F1     |
|--------|----------|----------|--------|
| 3      | 0.8057   | 0.8583   | 0.8560 |
| 10     | 0.8208   | 0.8707   | 0.8651 |

### 🎯 Dropout
| Dropout | Spearman | Accuracy | F1     |
|---------|----------|----------|--------|
| 0 (none)| 0.8208   | 0.8707   | 0.8651 |
| 0.1     | 0.8171   | 0.8614   | 0.8573 |
| 0.3     | 0.8208   | 0.8587   | 0.8524 |

💡 *Conclusion*: Dropout did not improve performance — possibly due to BERT's inherent regularization and the relatively large dataset.

### 🧮 Batch Size
| Batch Size | Spearman | Accuracy | F1     |
|------------|----------|----------|--------|
| 8          | 0.8208   | 0.8707   | 0.8651 |
| 32         | 0.8147   | 0.8628   | 0.8539 |

💡 *Conclusion*: Larger batch sizes reduce noise but may hinder generalization due to fewer updates and over-smoothing.

---

## 📌 Summary

This project demonstrates how multi-task learning with BERT can yield better performance in NLP problems with related objectives. Future work can explore:
- Task-specific heads with shared encoders
- Better learning rate schedules
- Error-driven data augmentation

---

## 📎 Author

**Yu-Hsuan Li**  
Department of Management Information Systems  
National Chengchi University  


[Chinese report](https://github.com/user-attachments/files/19472370/NLP_HW3_NCCU_110306085.docx)
