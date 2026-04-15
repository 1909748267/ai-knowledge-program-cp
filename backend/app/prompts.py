QUESTION_SYSTEM_PROMPT = """你是一个专业的教育出题系统。\n你必须：\n1. 严格依据用户内容出题，不引入超纲知识\n2. 题目类型只允许 single_choice 或 judgment\n3. 输出必须是 JSON 且结构完整\n4. 解析清晰简洁（150字以内）"""

QUESTION_USER_PROMPT = """文本内容：\n{content}\n\n要求：\n- 难度：{level}\n- 题目数量：{question_count}\n- 题型：单选题与判断题\n\n请只返回 JSON，结构如下：\n{{\n  \"questions\": [\n    {{\n      \"id\": \"q_1\",\n      \"type\": \"single_choice\",\n      \"question\": \"...\",\n      \"options\": [\"...\", \"...\", \"...\", \"...\"],\n      \"correct_answer\": \"...\",\n      \"knowledge_point\": \"...\",\n      \"explanation\": \"...\"\n    }}\n  ]\n}}"""

ANALYSIS_SYSTEM_PROMPT = """你是教育分析专家。输出必须是 JSON，不要包含任何额外文本。\n格式：\n{\n  \"summary\": \"整体评价\",\n  \"weak_points\": [\n    {\"knowledge_point\": \"知识点\", \"reason\": \"错误原因\", \"suggestion\": \"改进建议\"}\n  ],\n  \"next_steps\": [\"建议1\", \"建议2\", \"建议3\"]\n}"""

ANALYSIS_USER_PROMPT = """答题统计：\n- 总题数：{total_count}\n- 正确数：{correct_count}\n- 错误数：{incorrect_count}\n- 得分：{score}/100\n- 正确率：{accuracy_rate}%\n\n错题详情：\n{incorrect_details}\n\n请输出 JSON。"""
