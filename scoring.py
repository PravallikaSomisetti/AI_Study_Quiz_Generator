import os
import pandas as pd
from fpdf import FPDF

def calculate_score(quiz_data: list, user_answers: dict) -> tuple:
    score = 0
    detailed_results = []
    
    for idx, q in enumerate(quiz_data):
        user_ans = user_answers.get(idx)
        correct_ans = q["correct_answer"]
        is_correct = (user_ans == correct_ans)
        if is_correct:
            score += 1
            
        detailed_results.append({
            "Question ID": idx + 1,
            "Question": q["question"],
            "Your Answer": user_ans if user_ans else "[Unanswered]",
            "Correct Answer": correct_ans,
            "Is Correct": "Correct" if is_correct else "Incorrect",
            "Explanation": q.get("explanation", "")
        })
        
    return score, detailed_results

def export_csv(detailed_results: list) -> str:
    os.makedirs("downloads", exist_ok=True)
    csv_path = os.path.join("downloads", "quiz_results.csv")
    df = pd.DataFrame(detailed_results)
    df.to_csv(csv_path, index=False)
    return csv_path

def export_pdf(detailed_results: list, final_score: str) -> str:
    os.makedirs("downloads", exist_ok=True)
    pdf_path = os.path.join("downloads", "quiz_results.pdf")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "AI Study Quiz Generator - Performance Report", ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, f"Final Performance Score Metrics: {final_score}", ln=True)
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    for res in detailed_results:
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 6, f"Q{res['Question ID']}: {res['Question']}")
        
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 5, f"Your Input Choice: {res['Your Answer']}", ln=True)
        pdf.cell(0, 5, f"Validated Correct Answer: {res['Correct Answer']}", ln=True)
        
        if res["Is Correct"] == "Correct":
            pdf.set_text_color(0, 128, 0)
            pdf.cell(0, 5, "Status Assessment: Correct", ln=True)
        else:
            pdf.set_text_color(220, 20, 60)
            pdf.cell(0, 5, "Status Assessment: Incorrect", ln=True)
            
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "I", 9)
        pdf.multi_cell(0, 5, f"Context Trace: {res['Explanation']}")
        pdf.ln(4)
        
    pdf.output(pdf_path)
    return pdf_path