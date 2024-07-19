from src.DCD_sentiment_analyser.SentimentAnalyser import SentimentAnalyzer

# Example usage:
if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    modes = ["target_opinion_aspect_polarity", "polarity", "opinion_polarity"]
    texts = [
        "个头大、口感不错,就是个别坏了的或者有烂掉口子刻意用泥土封着,这样做不好。",
        "这真是太糟糕了。",
        "这部电影还不错。"
    ]

    for mode, text in zip(modes, texts):
        result = analyzer.analyze(mode, text)
        print(f"模式: {mode}")
        print(f"文本: {text}")
        print(f"结果: {result}")
