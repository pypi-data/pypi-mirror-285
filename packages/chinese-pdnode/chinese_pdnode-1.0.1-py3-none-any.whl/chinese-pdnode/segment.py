import jieba

def segment_text(text):
    """
    对输入的中文文本进行分词
    """
    return list(jieba.cut(text))
