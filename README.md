# 心理学实验研究应用

这是一个基于Python + Streamlit的Web应用，用于心理学实验研究。

## 功能特点

- **登录页面**：学生输入学生编号进入
- **自动分组**：1-60号学生为对照组，61-120号学生为实验组
- **对话界面**：
  - 实验组：使用罗杰斯人本主义风格的AI回复
  - 对照组：使用通用任务助手风格的AI回复
- **对话限制**：每人只能对话10轮
- **数据保存**：自动保存对话记录到本地CSV文件
- **管理员功能**：可编辑系统提示词，查看分组情况

## 本地运行

1. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

2. **运行应用**：
   ```bash
   streamlit run app.py
   ```

3. **访问应用**：打开浏览器访问 `http://localhost:8501`

## 部署到Streamlit Cloud

为了让学生可以通过网址访问应用，推荐部署到Streamlit Cloud：

### 部署步骤

1. **创建GitHub仓库**：
   - 在GitHub上创建一个新的仓库
   - 将项目文件（app.py, requirements.txt, config.json）上传到仓库

2. **部署到Streamlit Cloud**：
   - 访问 [Streamlit Cloud](https://streamlit.io/cloud)
   - 使用GitHub账号登录
   - 点击 "New app"
   - 选择你的GitHub仓库
   - 填写部署信息：
     - **Repository**：选择你的仓库
     - **Branch**：main
     - **Main file path**：app.py
   - 点击 "Deploy"

3. **配置环境变量**：
   - 在Streamlit Cloud的应用设置中，添加环境变量：
     - **API_KEY**：你的DeepSeek API密钥

4. **访问应用**：
   - 部署完成后，Streamlit Cloud会生成一个公共URL
   - 学生可以通过这个URL访问应用

## 管理员使用

1. **登录管理员控制台**：
   - 点击侧边栏的 "管理员控制台"
   - 输入密码：admin123

2. **编辑系统提示词**：
   - 在 "编辑系统提示词" 部分修改提示词
   - 点击 "保存提示词"

3. **查看分组情况**：
   - 在 "分组情况" 部分查看所有学生的分组信息

## 技术栈

- Python 3.8+
- Streamlit
- DeepSeek API
- Pandas

## 注意事项

- 确保DeepSeek API密钥有效
- 部署时注意保护API密钥，使用环境变量存储
- 定期备份 `data/chat_logs.csv` 文件，避免数据丢失
