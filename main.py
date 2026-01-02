import tkinter as tk
from constants import *
from quiz_data import quiz_data

root = tk.Tk()
root.title("Modern Quiz Application")
root.geometry("1000x600")
root.configure(bg=BG_MAIN)

# ---------------- GLOBAL STATE ----------------
current_category = None
current_question = 0
user_answers = []
time_left = 600

# ---------------- FRAMES ----------------
dashboard_frame = tk.Frame(root, bg=BG_MAIN)
quiz_frame = tk.Frame(root, bg=BG_MAIN)
dashboard_frame.pack(fill="both", expand=True)

# ---------------- HEADER ----------------
def create_header(parent, title, subtitle=""):
    h = tk.Frame(parent, bg=BG_MAIN)
    h.pack(fill="x", padx=30, pady=20)

    tk.Label(h, text=title, font=FONT_TITLE,
             fg=TEXT_DARK, bg=BG_MAIN).pack(side="left")

    if subtitle:
        tk.Label(h, text=subtitle, font=FONT_TEXT,
                 fg=TEXT_LIGHT, bg=BG_MAIN).pack(side="left", padx=15)

# ---------------- DASHBOARD ----------------
create_header(dashboard_frame, "Quiz Dashboard", "Choose a category")

cards = tk.Frame(dashboard_frame, bg=BG_MAIN)
cards.pack(pady=30)

def start_quiz(category):
    global current_category, current_question, user_answers, time_left
    current_category = category
    current_question = 0
    user_answers = []
    time_left = 600

    dashboard_frame.pack_forget()
    quiz_frame.pack(fill="both", expand=True)
    load_question()
    update_timer()

def create_card(parent, category):
    card = tk.Frame(parent, bg=CARD_BG, width=260, height=150)
    card.grid_propagate(False)

    tk.Label(card, text=category, font=FONT_CARD,
             fg=TEXT_DARK, bg=CARD_BG).pack(anchor="w", padx=20, pady=(20, 5))

    tk.Label(card, text="10 Questions • 10 Minutes",
             font=FONT_TEXT, fg=TEXT_LIGHT,
             bg=CARD_BG).pack(anchor="w", padx=20)

    tk.Button(card, text="Start Quiz →", font=FONT_BTN,
              bg=PRIMARY, fg="white", bd=0,
              command=lambda: start_quiz(category)
              ).pack(anchor="w", padx=20, pady=20)

    return card

r = c = 0
for cat in quiz_data:
    create_card(cards, cat).grid(row=r, column=c, padx=20, pady=20)
    c += 1
    if c == 3:
        c = 0
        r += 1

# ---------------- QUIZ SCREEN ----------------
create_header(quiz_frame, "Quiz In Progress")

top_bar = tk.Frame(quiz_frame, bg=BG_MAIN)
top_bar.pack(fill="x", padx=40)

progress_label = tk.Label(top_bar, font=FONT_TEXT,
                          fg=TEXT_LIGHT, bg=BG_MAIN)
progress_label.pack(side="left")

timer_label = tk.Label(top_bar, font=FONT_TEXT,
                       fg=DANGER, bg=BG_MAIN)
timer_label.pack(side="right")

card = tk.Frame(quiz_frame, bg=CARD_BG, padx=30, pady=30)
card.pack(pady=40)

question_label = tk.Label(card, font=FONT_CARD,
                          fg=TEXT_DARK, bg=CARD_BG,
                          wraplength=700, justify="left")
question_label.pack(anchor="w", pady=(0, 20))

answer_var = tk.StringVar()
option_buttons = []

for _ in range(4):
    rb = tk.Radiobutton(card, variable=answer_var,
                        font=FONT_TEXT, fg=TEXT_DARK,
                        bg=CARD_BG, anchor="w",
                        selectcolor=BG_MAIN)
    rb.pack(fill="x", pady=6)
    option_buttons.append(rb)

def next_question():
    user_answers.append(answer_var.get())
    global current_question
    current_question += 1

    if current_question < len(quiz_data[current_category]):
        load_question()
    else:
        quiz_frame.pack_forget()
        show_result_page()

tk.Button(card, text="Next →", font=FONT_BTN,
          bg=PRIMARY, fg="white",
          bd=0, padx=20, pady=8,
          command=next_question).pack(anchor="e", pady=20)

def load_question():
    q = quiz_data[current_category][current_question]

    question_label.config(text=q["question"])
    progress_label.config(
        text=f"Question {current_question + 1} of {len(quiz_data[current_category])}"
    )

    answer_var.set(None)
    for i, opt in enumerate(q["options"]):
        option_buttons[i].config(text=opt, value=opt)

def update_timer():
    global time_left
    if time_left > 0:
        mins = time_left // 60
        secs = time_left % 60
        timer_label.config(text=f"⏱ {mins:02d}:{secs:02d}")
        time_left -= 1
        root.after(1000, update_timer)
    else:
        quiz_frame.pack_forget()
        show_result_page()

# ---------------- RESULT PAGE ----------------
def show_result_page():
    result = tk.Toplevel(root)
    result.title("Quiz Result")
    result.geometry("900x600")
    result.configure(bg=BG_MAIN)

    total = len(quiz_data[current_category])
    correct = sum(
        1 for i, q in enumerate(quiz_data[current_category])
        if i < len(user_answers) and user_answers[i] == q["answer"]
    )
    wrong = total - correct
    accuracy = int((correct / total) * 100)

    create_header(result, "Result Overview")

    summary = tk.Frame(result, bg=BG_MAIN)
    summary.pack(pady=20)

    def stat(title, value, color):
        c = tk.Frame(summary, bg=CARD_BG, width=180, height=100)
        c.pack_propagate(False)
        c.pack(side="left", padx=15)
        tk.Label(c, text=title, fg=TEXT_LIGHT,
                 bg=CARD_BG, font=FONT_TEXT).pack(pady=(20, 5))
        tk.Label(c, text=value, fg=color,
                 bg=CARD_BG, font=FONT_CARD).pack()

    stat("Total", total, TEXT_DARK)
    stat("Correct", correct, SUCCESS)
    stat("Wrong", wrong, DANGER)
    stat("Accuracy", f"{accuracy}%", PRIMARY)

    report = tk.Frame(result, bg=BG_MAIN)
    report.pack(fill="both", expand=True, padx=30, pady=20)

    canvas = tk.Canvas(report, bg=BG_MAIN, highlightthickness=0)
    scrollbar = tk.Scrollbar(report, command=canvas.yview)
    scrollable = tk.Frame(canvas, bg=BG_MAIN)

    scrollable.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for i, q in enumerate(quiz_data[current_category]):
        f = tk.Frame(scrollable, bg=CARD_BG, padx=20, pady=15)
        f.pack(fill="x", pady=10)

        tk.Label(f, text=f"Q{i+1}: {q['question']}",
                 font=FONT_TEXT, fg=TEXT_DARK,
                 bg=CARD_BG, wraplength=750).pack(anchor="w")

        user_ans = user_answers[i] if i < len(user_answers) else "Not Answered"

        tk.Label(f, text=f"Your Answer: {user_ans}",
                 fg=DANGER if user_ans != q["answer"] else SUCCESS,
                 bg=CARD_BG, font=FONT_TEXT).pack(anchor="w", pady=3)

        tk.Label(f, text=f"Correct Answer: {q['answer']}",
                 fg=SUCCESS, bg=CARD_BG,
                 font=FONT_TEXT).pack(anchor="w")

root.mainloop()
