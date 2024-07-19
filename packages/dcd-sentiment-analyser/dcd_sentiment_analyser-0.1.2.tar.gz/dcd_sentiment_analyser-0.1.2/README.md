# SentimentAnalyzer

SentimentAnalyzer 是一个情感分析工具包，基于 T5 模型，支持多种自然语言任务。用户可以选择不同的提取模式，轻松完成情感四元组、二元组、三元组等任务。

## 安装

你可以通过以下命令安装 SentimentAnalyzer：

```bash
pip install dcd-sentiment-analyzer
```

## 使用方法

### 快速开始

首先，导入并初始化 `SentimentAnalyzer` 类：

```python
from DCD_sentiment_analyser import SentimentAnalyzer

analyzer = SentimentAnalyzer() # 自动下载模型文件
# 可以传入自定义模型目录用于初始化SentimentAnalyzer类
analyzer = SentimentAnalyzer(model_dir="your_model_dir")
```

### 模式选择

`SentimentAnalyzer` 支持以下提取模式：

- `target_opinion_aspect_polarity` (对象 | 观点 | 方面 | 极性)
- `object_opinion` (对象 | 观点)
- `object_opinion_aspect` (对象 | 观点 | 方面)
- `object_opinion_polarity` (对象 | 观点 | 极性)
- `object_aspect_polarity` (对象 | 方面 | 极性)
- `aspect_polarity` (方面 | 极性)
- `opinion_polarity` (观点 | 极性)
- `polarity` (极性)

### 例子

#### 例子1: 四元组提取

```python
text = "个头大、口感不错,就是个别坏了的或者有烂掉口子刻意用泥土封着,这样做不好。"
result = analyzer.analyze("quadruples", text)
print(result)
```

#### 例子2: 情感极性判断

```python
text = "这真是太糟糕了。"
result = analyzer.analyze("polarity", text)
print(result)
```

#### 例子3: 观点与极性提取

```python
text = "这部电影还不错。"
result = analyzer.analyze("opinion_polarity", text)
print(result)
```

## 运行环境

- Python 3.8+
- PyTorch
- Transformers

## 联系方式

如有任何问题，请联系 [younghangx@163.com](mailto:your_email@example.com)。

## 许可证

此项目基于 MIT 许可证，详细请查看 [LICENSE](LICENSE) 文件。