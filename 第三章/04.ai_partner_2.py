import streamlit as st
import os
from openai import OpenAI
from openai.resources.skills import content
import datetime
from streamlit.runtime.state import session_state
import json

# 基础目录（适配本地运行和Streamlit Cloud部署）
BASE_DIR = "第三章" if os.path.exists("第三章") else ""

# 设置页面配置项
st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="💗",
    # 页面布局
    layout="wide",
    #侧边栏
    initial_sidebar_state="auto",
    menu_items={}
)

#定义保存会话的函数
def save_session():
    if st.session_state.current_session:
        #构建新的会话对象
        session_date = {
            "nick_name": st.session_state.nick_name,
            "character": st.session_state.character,
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages
        }
        #如果session目录不存在，则创建
        if not os.path.exists(f"{BASE_DIR}/sessions"):
            os.makedirs(f"{BASE_DIR}/sessions", exist_ok=True)
        #保存当前会话
        with open(f"{BASE_DIR}/sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
            json.dump(session_date, f, ensure_ascii=False, indent=2)

#保存背景设置的函数
def save_background_settings():
    settings = {
        "background_image": st.session_state.get("background_image", None),
        "background_opacity": st.session_state.get("background_opacity", 1.0)
    }
    if not os.path.exists(f"{BASE_DIR}/resources"):
        os.makedirs(f"{BASE_DIR}/resources", exist_ok=True)
    with open(f"{BASE_DIR}/resources/background_settings.json", "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

#加载背景设置的函数
def load_background_settings():
    default_settings = {
        "background_image": None,
        "background_opacity": 1.0
    }
    try:
        if os.path.exists(f"{BASE_DIR}/resources/background_settings.json"):
            with open(f"{BASE_DIR}/resources/background_settings.json", "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default_settings

#生成会话标识的函数
def generate_session_name():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

#加载所有会话列表的函数
def load_sessions():
    sessions_list = []
    #加载sessions下的文件
    if os.path.exists(f"{BASE_DIR}/sessions"):
        file_list = os.listdir(f"{BASE_DIR}/sessions")
        for filename in file_list:
            if filename.endswith(".json"):
                sessions_list.append(filename[:-5])
    return sorted(sessions_list, reverse=True)

#加载指定的会话的函数
def load_session(session_name):
    try:
        if os.path.exists(f"{BASE_DIR}/sessions/{session_name}.json"):
            # 加载会话数据
            with open(f"{BASE_DIR}/sessions/{session_name}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.messages = session_data["messages"]
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.character = session_data["character"]
                st.session_state.current_session = session_name
    except Exception:
        st.error(f"加载会话失败!")

#删除会话的函数
def delete_session(session_name):
    try:
        if os.path.exists(f"{BASE_DIR}/sessions/{session_name}.json"):
            os.remove(f"{BASE_DIR}/sessions/{session_name}.json")#删除文件
            #如果删除的是当前会话，则需要更新会话列表
            if session_name == st.session_state.current_session:
                st.session_state.messages = []
                st.session_state.current_session = generate_session_name()

    except Exception:
        st.error(f"删除会话失败!")


#大标题
st.title("AI智能伴侣")
# logo
st.logo(f"{BASE_DIR}/resources/aixin logo.png")

#初始化聊天信息
if "messages" not in st.session_state:
    st.session_state.messages = []

#昵称
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "胡桃"
#性格
if "character" not in st.session_state:
    st.session_state.character = "活泼开朗的《原神》少女角色"

#会话标识
if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()

#背景设置
if "background_image" not in st.session_state:
    bg_settings = load_background_settings()
    st.session_state.background_image = bg_settings.get("background_image", None)
if "background_opacity" not in st.session_state:
    bg_settings = load_background_settings()
    st.session_state.background_opacity = bg_settings.get("background_opacity", 1.0)

#系统提示词
system_prompt = """
        你叫%s，现在是用户的真实伴倡，请完全代入伴侣角色。:
        规则:
            1.每次只回1条消息
            2.禁止任何场景或状态描述性文字
            3.匹配用户的语言
            4.回复简短，像微信聊天一样
            5.有需要的话可以用emoji表情
            6.用符合伴侣性格的方式对话
            7.回复的内容,要充分体现伴侣的性格特征
        伴侣性格:
            %s
        你必须严格遵守上述规则来回复用户。
"""

#应用背景图和透明度
bg_css = ""
if st.session_state.background_image:
    opacity = st.session_state.background_opacity
    # 计算内容区域的背景色（白色带透明度）
    content_bg = f"rgba(255, 255, 255, {opacity})"
    bg_css = f"""
    <style>
    /* 设置整个页面的背景图 */
    .stApp {{
        background: linear-gradient(rgba(255,255,255,{opacity}), rgba(255,255,255,{opacity})), 
                    url("data:image/png;base64,{st.session_state.background_image}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    /* 设置主内容区域透明 */
    [data-testid="stAppViewContainer"] {{
        background-color: transparent !important;
    }}
    [data-testid="stHeader"] {{
        background-color: transparent !important;
    }}
    /* 设置侧边栏半透明 */
    section[data-testid="stSidebar"] {{
        background-color: rgba(30, 30, 30, {opacity * 0.8}) !important;
    }}
    section[data-testid="stSidebar"] > div {{
        background-color: transparent !important;
    }}
    /* 设置底部区域的背景为半透明（输入框周围的深色区域）*/
    [data-testid="stBottom"],
    .stApp footer,
    div[data-testid="bottom-container"] {{
        background-color: rgba(30, 30, 30, {opacity * 0.6}) !important;
    }}
    /* 保持输入框本身不透明 */
    [data-testid="stChatInput"] {{
        background-color: rgba(40, 40, 40, 0.9) !important;
    }}
    /* --- 移动端背景样式适配 --- */
    @media (max-width: 768px) {{
        .stApp {{
            background-attachment: scroll !important;
            background-position: center top !important;
        }}
        section[data-testid="stSidebar"] {{
            background-color: rgba(20, 20, 20, 0.95) !important;
        }}
        [data-testid="stBottom"],
        .stApp footer,
        div[data-testid="bottom-container"] {{
            background-color: rgba(20, 20, 20, 0.85) !important;
            padding: 6px 8px !important;
        }}
        [data-testid="stChatInput"] {{
            background-color: rgba(40, 40, 40, 0.95) !important;
        }}
    }}
    </style>
    """
else:
    bg_css = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-color: rgba(255, 255, 255, {st.session_state.background_opacity}) !important;
    }}
    /* --- 移动端无背景时的适配 --- */
    @media (max-width: 768px) {{
        [data-testid="stAppViewContainer"] {{
            background-color: rgba(255, 255, 255, {min(st.session_state.background_opacity, 0.95)}) !important;
        }}
    }}
    </style>
    """
st.markdown(bg_css, unsafe_allow_html=True)

# ===== 移动端响应式适配CSS =====
mobile_css = """
<style>
/* ===== 移动端全局响应式适配 ===== */

/* --- 全局防溢出（所有屏幕尺寸生效） --- */
html, body {
    overflow-x: hidden !important;
    max-width: 100vw !important;
}
.stApp {
    overflow-x: hidden !important;
    max-width: 100vw !important;
}
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stVerticalBlock"] {
    overflow-x: hidden !important;
    max-width: 100% !important;
}

/* --- 768px以下：平板及手机通用适配 --- */
@media (max-width: 768px) {
    /* ===== 1. 侧边栏默认收起（移动端自动折叠） ===== */
    /* 隐藏侧边栏展开触发区域的默认展开状态，强制收起 */
    [data-testid="stSidebar"] {
        width: auto !important;
        min-width: 0 !important;
        transition: transform 0.3s ease !important;
    }
    /* 侧边栏导航按钮区域适配 */
    [data-testid="stSidebarNav"] {
        width: 100% !important;
    }

    /* ===== 2. 按钮与输入框宽度适配 ===== */
    /* 侧边栏按钮宽度不超过90%容器 */
    section[data-testid="stSidebar"] button,
    section[data-testid="stSidebar"] [data-testid="stButton"] {
        max-width: 90% !important;
        width: 90% !important;
        min-height: 40px !important;
        font-size: 14px !important;
        padding: 8px 12px !important;
    }
    /* 主界面chat_input宽度100%减去边距 */
    [data-testid="stChatInput"] {
        width: calc(100% - 16px) !important;
        margin: 0 8px !important;
        max-width: calc(100% - 16px) !important;
    }
    [data-testid="stChatInput"] > div {
        width: 100% !important;
    }
    /* 侧边栏输入框宽度适配 */
    section[data-testid="stSidebar"] input[type="text"],
    section[data-testid="stSidebar"] textarea {
        width: 90% !important;
        max-width: 90% !important;
        font-size: 14px !important;
        min-height: 36px !important;
    }

    /* ===== 3. 字体大小优化 ===== */
    /* 标题字体 1.5-2rem，清晰可见 */
    .stApp h1 {
        font-size: 1.75rem !important;
        margin-bottom: 0.5rem !important;
    }
    /* 二级标题适配 */
    .stApp h2, .stApp h3 {
        font-size: 1.1rem !important;
    }
    /* 聊天消息文字：1rem(16px)，行高1.5，阅读舒适 */
    [data-testid="stChatMessageContent"] {
        font-size: 1rem !important;
        line-height: 1.5 !important;
    }
    /* 侧边栏标签字体 0.9rem */
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stSubheader,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    section[data-testid="stSidebar"] caption {
        font-size: 0.9rem !important;
    }
    /* iOS设备：输入框文字至少16px，避免系统自动缩放 */
    [data-testid="stChatInput"] textarea,
    [data-testid="stChatInput"] input {
        font-size: 16px !important;
        max-height: 120px !important;
    }

    /* ===== 4. 聊天气泡与头像适配 ===== */
    [data-testid="stChatMessage"] {
        max-width: 92% !important;
        padding: 0.5rem 0.75rem !important;
        margin-bottom: 0.3rem !important;
    }
    [data-testid="stChatMessageAvatar"] {
        width: 28px !important;
        height: 28px !important;
        min-width: 28px !important;
    }

    /* ===== 5. 其他组件适配 ===== */
    /* 侧边栏滑块适配 */
    section[data-testid="stSidebar"] [data-testid="stSlider"] {
        padding: 0.5rem 0 !important;
        width: 90% !important;
    }
    /* 侧边栏内间距优化 */
    section[data-testid="stSidebar"] .block-container {
        padding: 1rem 0.75rem !important;
    }
    /* 底部输入区域：避免遮挡聊天内容 */
    [data-testid="stBottom"] {
        min-height: auto !important;
    }
    /* 小号文字适配 */
    .stApp small,
    .stApp [data-testid="stText"] {
        font-size: 12px !important;
    }
    /* 主内容区域内间距优化 */
    [data-testid="stAppViewContainer"] .block-container {
        padding: 1rem 0.75rem !important;
    }
    /* 会话列表列宽适配 */
    section[data-testid="stSidebar"] [data-testid="column"] {
        flex: 0 0 auto !important;
        min-width: 0 !important;
    }
    /* 文件上传器宽度适配 */
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
        width: 90% !important;
    }
    /* 确保所有容器不溢出 */
    [data-testid="stAppViewContainer"] {
        overflow-x: hidden !important;
    }
}

/* --- 480px以下：小屏手机深度适配 --- */
@media (max-width: 480px) {
    /* 标题进一步缩小但保持可读 */
    .stApp h1 {
        font-size: 1.5rem !important;
    }
    /* 聊天气泡几乎占满宽度 */
    [data-testid="stChatMessage"] {
        max-width: 96% !important;
        padding: 0.4rem 0.5rem !important;
    }
    [data-testid="stChatMessageContent"] {
        font-size: 1rem !important;  /* 保持1rem确保可读性 */
        line-height: 1.5 !important;
    }
    /* 头像进一步缩小 */
    [data-testid="stChatMessageAvatar"] {
        width: 24px !important;
        height: 24px !important;
        min-width: 24px !important;
    }
    /* 侧边栏按钮更大触摸区域 */
    section[data-testid="stSidebar"] button,
    section[data-testid="stSidebar"] [data-testid="stButton"] {
        min-height: 44px !important;
        font-size: 13px !important;
        max-width: 95% !important;
        width: 95% !important;
    }
    /* 输入框确保16px防缩放 */
    [data-testid="stChatInput"] textarea,
    [data-testid="stChatInput"] input {
        font-size: 16px !important;
    }
    /* chat_input进一步优化 */
    [data-testid="stChatInput"] {
        width: calc(100% - 10px) !important;
        margin: 0 5px !important;
        max-width: calc(100% - 10px) !important;
    }
    /* 主内容区域紧凑内间距 */
    [data-testid="stAppViewContainer"] .block-container {
        padding: 0.75rem 0.5rem !important;
    }
    /* 侧边栏标签在小屏上保持可读 */
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stSubheader {
        font-size: 0.85rem !important;
    }
}
</style>
"""
st.markdown(mobile_css, unsafe_allow_html=True)

#展示聊天信息
st.text(f"会话名称：{st.session_state.current_session}")
for message in st.session_state.messages:# {"role": "user", "content": prompt}
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    else:
        st.chat_message("assistant").write(message["content"])

# 创建与AI大模型交互的客户端对象（DEEPSEEK_API_KEY 环境变量的名字，值就是Deep Seek的API_KEY的值）
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'),base_url="https://api.deepseek.com")

#左侧侧边栏
with st.sidebar:#---with, 创建一个上下文管理器，可以在with内部执行代码，并在with外部执行代码
    #ai控制面板
    st.subheader("AI控制面板")
    #新建会话按钮
    if st.button("新建会话", type="primary", icon="💗", width="stretch"):
        #1.保存当前会话
        save_session()
        #2.创建新的会话
        if st.session_state.messages:#若当前会话非空，则保存当前会话信息
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()
            save_session()
            st.rerun()  # 重新运行当前页面

    #会话历史
    st.text("会话历史")
    session_list = load_sessions()
    for session in session_list:
        col1, col2 = st.columns([4, 1])
        with col1:
            #加载会话信息
            #三元运算符:如果条件为真，则返回第一个表达式的值，否则返回第二个表达式的值--->语法：条件?表达式1:表达式2
            if st.button(session, width="stretch", icon="💌", key=f"load_{session}",type="primary" if session == st.session_state.current_session else "secondary"):
                load_session(session)
                st.rerun()

        with col2:
            #删除会话信息
            if st.button("", width="stretch", icon="❌", key=f"delete_{session}"):
                delete_session(session)
                st.rerun()
    #分割线
    st.divider()

    st.subheader("伴侣信息")
    #昵称输入框
    nick_name = st.text_input("昵称",placeholder="请输入昵称",value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name
    #性格输入框
    character = st.text_area("性格",placeholder="请输入伴侣性格",value=st.session_state.character)
    if character:
        st.session_state.character = character
    
    #分割线
    st.divider()
    
    #换背景功能
    st.subheader("换背景")
    #上传背景图
    uploaded_file = st.file_uploader("上传背景图", type=["png", "jpg", "jpeg"], key="bg_uploader")
    if uploaded_file is not None:
        #读取上传的图片
        image_bytes = uploaded_file.read()
        import base64
        image_base64 = base64.b64encode(image_bytes).decode()
        st.session_state.background_image = image_base64
        #保存图片到resources目录
        with open(ff"{BASE_DIR}/resources/custom_background.png", "wb") as f:
            f.write(image_bytes)
        save_background_settings()
        st.success("背景图已更新！")
        # 不调用 rerun，让页面自然刷新
    
    #如果有背景图，显示删除按钮
    if st.session_state.background_image:
        if st.button("删除背景图", icon="❌", width="stretch"):
            st.session_state.background_image = None
            #删除保存的背景图文件
            if os.path.exists(f"{BASE_DIR}/resources/custom_background.png"):
                os.remove(f"{BASE_DIR}/resources/custom_background.png")
            save_background_settings()
            st.rerun()
    
    #透明度调节
    st.markdown("**背景透明度**")
    opacity = st.slider("", min_value=0.0, max_value=1.0, value=st.session_state.background_opacity, step=0.05, label_visibility="collapsed")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption(f"当前值: {opacity:.2f} (0.0=完全透明, 1.0=完全不透明)")
    with col2:
        if st.button("应用", key="apply_opacity", use_container_width=True):
            if opacity != st.session_state.background_opacity:
                st.session_state.background_opacity = opacity
                save_background_settings()
                st.rerun()


#消息输入框
prompt =  st.chat_input("请输入你的问题")
if prompt:
    st.chat_message("user").write(prompt)
    print( "调用AI大模型，提示词------>",prompt)
    # 保存用户提示词
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 调用ai大模型
    # 与Ai大模型进行交互
    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content": system_prompt % (st.session_state.nick_name,st.session_state.character)},
            *st.session_state.messages
        ],
        stream=True,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )
    # 输出大模型返回的结果(非流式输出的解析方式)
    #print("<------大模型返回的结果",response.choices[0].message.content)
    #st.chat_message("assistant").write(response.choices[0].message.content)

    # 输出大模型返回的结果(流式输出的解析方式)
    response_message = st.empty () #创建一个空的组件，用来保存大模型返回的结果
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            response_message.chat_message("assistant").write(full_response)

    #保存大模型返回的结果
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    #保存会话信息
    save_session()