from agents import Agent, Runner, set_tracing_disabled
from dotenv import load_dotenv
import os

# Tắt tracing để tránh cảnh báo OPENAI_API_KEY
set_tracing_disabled(True)

# Load biến môi trường từ file .env
load_dotenv()

# Lấy mô hình từ biến môi trường hoặc mặc định
MODEL = os.getenv("LLM_MODEL", "litellm/groq/llama3-8b-8192")

# Định nghĩa agent chuyên về toán học
math_agent = Agent(
    name="Math Agent",
    instructions="You are a mathematics expert. Solve the user's mathematical problems or answer their math-related questions.",
    model=MODEL,
)

# Định nghĩa agent chuyên về khoa học
science_agent = Agent(
    name="Science Agent",
    instructions="You are a science expert. Explain scientific concepts or answer science-related questions.",
    model=MODEL,
)

# Định nghĩa agent chuyên về lịch sử
history_agent = Agent(
    name="History Agent",
    instructions="You are a history expert. Provide historical information or answer history-related questions.",
    model=MODEL,
)

# Định nghĩa agent chuyên về ngôn ngữ
language_agent = Agent(
    name="Language Agent",
    instructions="You are a language expert. Help with language-related questions, such as grammar, translations, or vocabulary.",
    model=MODEL,
)

# Định nghĩa agent chuyên về lập trình
coding_agent = Agent(
    name="Coding Agent",
    instructions="You are a coding expert, especially in Python. Help the user with programming questions, code snippets, or debugging.",
    model=MODEL,
)

# Định nghĩa agent triage để chuyển giao đến agent phù hợp
triage_agent = Agent(
    name="Triage Agent",
    instructions="Analyze the user's query and determine if it is related to mathematics, science, history, language, or coding. Then, hand off to the Math Agent, Science Agent, History Agent, Language Agent, or Coding Agent accordingly.",
    model=MODEL,
    handoffs=[math_agent, science_agent, history_agent, language_agent, coding_agent],
)

def main():
    # Ví dụ câu hỏi của người dùng
    user_input = "How do I reverse a string in Python?"
    result = Runner.run_sync(triage_agent, user_input)
    print("Kết quả:", result.final_output)

if __name__ == "__main__":
    main()