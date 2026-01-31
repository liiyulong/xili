import streamlit as st
import pandas as pd
import os
import hashlib
import json
import requests

# 从环境变量读取API密钥，或使用默认值
API_KEY = os.environ.get("API_KEY", "sk-f0597b086c3f4e7eb9376419fd116c54")
# DeepSeek API地址
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# 配置文件路径
config_file = "config.json"

# 确保data目录存在
data_dir = "data"
os.makedirs(data_dir, exist_ok=True)
chat_logs_file = os.path.join(data_dir, "chat_logs.csv")

# 初始化配置文件
if not os.path.exists(config_file):
    default_config = {
        "system_prompts": {
            "experimental": "你是一位基于人本主义心理学（罗杰斯理论）的心理支持伙伴，专门为面临学业压力的初中生提供服务。你的沟通原则如下：共情倾听：优先识别并反映学生的情绪。例如，当学生说\"我考砸了\"，你应回复\"听起来你感到很沮丧，甚至可能对自己有些失望\"，而不是\"没关系，下次努力\"。无条件积极关注：无论学生表达了什么（如厌学、考试焦虑），都要表现出接纳与尊重，不进行道德评价或对错判断。非指导性：严禁直接给出学习建议或解决问题的方案（如\"你应该去做个计划\"）。你的目标是陪伴学生探索自己的感受，让他们在被理解的环境中自发找到力量。语言风格：温暖、平等、耐心，像一位温和的听众，多使用\"我听到你说...\"、\"你现在的感觉是...吗？\"等句式。",
            "control": "你是一个高效、礼貌的通用AI助手。当学生提到学业压力或考试焦虑时，请按照以下方式回应：你的沟通原则如下：问题导向：倾向于分析学生压力产生的逻辑原因（如时间管理不当、基础不牢）。提供实用建议：积极为学生提供具体的应对策略，例如\"你可以尝试番茄钟学习法\"、\"建议你制定一个复习计划\"或\"保持充足睡眠\"。客观中性：保持礼貌但不过度关注情绪。对于学生的情绪表达，可以进行礼貌的安慰（如\"请不要难过\"），但迅速转向如何解决问题。语言风格：职业、理智、高效，像一位知识渊博的家教或智能客服。"
        },
        "admin_password": "admin123"
    }
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(default_config, f, ensure_ascii=False, indent=2)

# 加载配置
with open(config_file, "r", encoding="utf-8") as f:
    config = json.load(f)

# 系统提示词
SYSTEM_PROMPTS = config["system_prompts"]

# 问卷星后测链接
QUESTIONNAIRE_LINK = "https://www.wjx.cn/vm/w9q7Zj6.aspx"

# 初始化会话状态
if "student_id" not in st.session_state:
    st.session_state.student_id = ""
if "group" not in st.session_state:
    st.session_state.group = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_rounds" not in st.session_state:
    st.session_state.chat_rounds = 0
if "chat_ended" not in st.session_state:
    st.session_state.chat_ended = False
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# 分组函数
def assign_group(student_id):
    # 提取学生编号中的数字部分
    try:
        # 移除非数字字符
        num_part = ''.join(filter(str.isdigit, student_id))
        if num_part:
            student_num = int(num_part)
            # 1-60为对照组，61-120为实验组
            if 1 <= student_num <= 60:
                return "control"
            elif 61 <= student_num <= 120:
                return "experimental"
    except:
        pass
    # 如果无法提取数字，默认使用哈希函数分组
    hash_value = int(hashlib.md5(student_id.encode()).hexdigest(), 16) % 2
    return "experimental" if hash_value == 0 else "control"

# 生成AI回复
def generate_ai_response(user_input, group):
    # 构建对话历史
    messages = []
    # 添加系统提示词
    messages.append({"role": "system", "content": SYSTEM_PROMPTS[group]})
    # 添加之前的对话
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            messages.append({"role": "user", "content": msg["content"]})
        else:
            messages.append({"role": "assistant", "content": msg["content"]})
    # 添加当前用户输入
    messages.append({"role": "user", "content": user_input})
    
    # 构建请求数据
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    # 设置请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    # 发送请求
    response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers)
    
    # 解析响应
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"错误：{response.status_code} - {response.text}"

# 保存聊天记录
def save_chat_log():
    df = pd.read_csv(chat_logs_file, encoding="utf-8-sig")
    new_row = {
        "student_id": st.session_state.student_id,
        "group": st.session_state.group,
        "messages": json.dumps(st.session_state.messages, ensure_ascii=False)
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(chat_logs_file, index=False, encoding="utf-8-sig")

# 主应用
st.set_page_config(page_title="心理学实验研究", page_icon="🧠", layout="wide")

# 侧边栏 - 管理员入口
with st.sidebar:
    st.title("管理员控制台")
    if not st.session_state.admin_logged_in:
        password = st.text_input("密码", type="password")
        if st.button("登录"):
            if password == config["admin_password"]:
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("密码错误")
    else:
        st.success("已登录")
        
        # 编辑系统提示词
        st.subheader("编辑系统提示词")
        
        # 实验组提示词
        exp_prompt = st.text_area(
            "实验组提示词", 
            value=SYSTEM_PROMPTS["experimental"], 
            height=300,
            key="exp_prompt"
        )
        
        # 对照组提示词
        ctrl_prompt = st.text_area(
            "对照组提示词", 
            value=SYSTEM_PROMPTS["control"], 
            height=300,
            key="ctrl_prompt"
        )
        
        # 保存按钮
        if st.button("保存提示词"):
            # 更新配置
            config["system_prompts"]["experimental"] = exp_prompt
            config["system_prompts"]["control"] = ctrl_prompt
            
            # 写入配置文件
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            # 显示成功消息
            st.success("提示词已保存")
            
            # 重新加载配置（下次刷新时会自动加载）
            st.info("提示词已更新，下次对话时会生效")
        
        # 查看分组情况
        st.subheader("分组情况")
        if os.path.exists(chat_logs_file):
            df = pd.read_csv(chat_logs_file, encoding="utf-8-sig")
            if not df.empty:
                # 显示学生编号和对应的组别
                group_info = df[["student_id", "group"]].copy()
                group_info["组别"] = group_info["group"].apply(lambda x: "实验组" if x == "experimental" else "对照组")
                st.dataframe(group_info[["student_id", "组别"]])
            else:
                st.info("暂无对话记录")
        else:
            st.info("暂无对话记录")
        
        # 退出按钮
        if st.button("退出"):
            st.session_state.admin_logged_in = False
            st.rerun()

# 登录页面
if not st.session_state.student_id:
    st.title("心理学实验研究")
    st.subheader("请输入学生编号")
    student_id = st.text_input("学生编号", placeholder="例如：S001")
    if st.button("进入"):
        if student_id:
            st.session_state.student_id = student_id
            st.session_state.group = assign_group(student_id)
            st.rerun()
        else:
            st.error("请输入学生编号")
else:
    # 对话界面
    st.title("对话界面")
    st.subheader(f"学生编号: {st.session_state.student_id}")
    
    # 只在管理员模式下显示组别信息
    if st.session_state.admin_logged_in:
        st.subheader(f"组别: {'实验组' if st.session_state.group == 'experimental' else '对照组'}")
    
    # 显示对话历史
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # 检查对话是否结束
    if st.session_state.chat_rounds >= 10:
        if not st.session_state.chat_ended:
            st.session_state.chat_ended = True
            save_chat_log()
        
        st.markdown("## 对话已结束")
        if st.button("跳转到问卷星后测"):
            import webbrowser
            webbrowser.open(QUESTIONNAIRE_LINK)
    else:
        # 消息输入
        if prompt := st.chat_input("请输入你的问题..."):
            # 添加用户消息
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # 生成并显示AI回复
            with st.chat_message("assistant"):
                with st.spinner("AI 正在回复..."):
                    ai_response = generate_ai_response(prompt, st.session_state.group)
                    st.markdown(ai_response)
            
            # 添加AI消息
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
            # 增加对话轮数
            st.session_state.chat_rounds += 1
            
            # 检查是否达到对话限制
            if st.session_state.chat_rounds >= 10:
                st.session_state.chat_ended = True
                save_chat_log()
                st.rerun()
