import os
import torch
from transformers import T5Tokenizer, AutoModelForSeq2SeqLM, GenerationConfig


class SentimentAnalyzer:
    def __init__(self, model_path="yuyijiong/T5-large-sentiment-analysis-Chinese-MultiTask"):
        os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
        self.tokenizer = T5Tokenizer.from_pretrained(model_path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path, device_map="auto")
        self.generation_config = GenerationConfig.from_pretrained(model_path)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def analyze(self, mode, text):
        task_mapping = {
            "target_opinion_aspect_polarity": "情感四元组(对象 | 观点 | 方面 | 极性)抽取任务:",
            "target_opinion": "情感二元组(对象 | 观点)抽取任务:",
            "target_opinion_aspect": "情感三元组(对象 | 观点 | 方面)抽取任务:",
            "target_opinion_polarity": "情感三元组(对象 | 观点 | 极性)抽取任务:",
            "target_aspect_polarity": "情感三元组(对象 | 方面 | 极性)抽取任务:",
            "aspect_polarity": "情感二元组(方面 | 极性)抽取任务:",
            "opinion_polarity": "情感二元组(观点 | 极性)抽取任务:",
            "polarity": "判断以下评论的情感极性:"
        }

        if mode not in task_mapping:
            raise ValueError(f"Unsupported mode '{mode}'. Supported modes are: {list(task_mapping.keys())}")

        task = task_mapping[mode]
        formatted_text = f"{task}[{text}]"

        input_ids = self.tokenizer(formatted_text, return_tensors="pt", padding=True)['input_ids'].to(self.device)
        with torch.no_grad():
            output = self.model.generate(input_ids=input_ids, generation_config=self.generation_config)

        output_str = self.tokenizer.batch_decode(output, skip_special_tokens=True)
        return output_str[0]
