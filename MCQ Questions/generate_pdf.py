from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import re

def generate_pdf():
    output_file = "Assessment.pdf"
    
    # 1. Parse Questions
    questions = []
    with open("QualtricsImport.txt", "r") as f:
        content = f.read()
        
    # Split by [[Question:MC]]
    # The file starts with [[AdvancedFormat]], so skip that
    q_blocks = content.split("[[Question:MC]]")
    
    for block in q_blocks:
        if not block.strip() or "[[AdvancedFormat]]" in block:
            continue
            
        q_data = {}
        
        # Extract ID
        id_match = re.search(r'\[\[ID:(Q\d+)\]\]', block)
        if id_match:
            q_data['id'] = id_match.group(1)
        else:
            continue
            
        # Extract Text
        # Text is between ID line and [[Choices]]
        # Or between Question:MC and [[Choices]] if ID is missing (but we found ID)
        
        # Let's split by lines to be safer
        lines = block.strip().split('\n')
        q_text_lines = []
        choices = []
        state = "TEXT"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith("[[ID:"):
                continue
            if line == "[[Choices]]":
                state = "CHOICES"
                continue
            
            if state == "TEXT":
                q_text_lines.append(line)
            elif state == "CHOICES":
                choices.append(line)
                
        q_data['text'] = " ".join(q_text_lines)
        q_data['choices'] = choices
        questions.append(q_data)
        
    # 2. Parse Answers
    answers = {}
    with open("AnswerKey.md", "r") as f:
        lines = f.readlines()
        
    for line in lines:
        if not line.startswith("| Q"):
            continue
        parts = [p.strip() for p in line.split('|')]
        # parts[0] is empty, parts[1] is ID, parts[2] is Answer, parts[3] is Rationale
        if len(parts) >= 4:
            qid = parts[1]
            ans = parts[2]
            rat = parts[3]
            answers[qid] = {'answer': ans, 'rationale': rat}
            
    # 3. Generate PDF
    doc = BaseDocTemplate(output_file, pagesize=letter)
    
    # Two columns
    frame1 = Frame(0.5*inch, 0.5*inch, 3.5*inch, 10*inch, id='col1')
    frame2 = Frame(4.25*inch, 0.5*inch, 3.5*inch, 10*inch, id='col2')
    
    template = PageTemplate(id='TwoCol', frames=[frame1, frame2])
    doc.addPageTemplates([template])
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='QuestionText', parent=styles['Normal'], spaceAfter=6, fontSize=10, leading=12))
    styles.add(ParagraphStyle(name='ChoiceText', parent=styles['Normal'], leftIndent=15, spaceAfter=2, fontSize=10, leading=12))
    styles.add(ParagraphStyle(name='Header1', parent=styles['Heading1'], alignment=1, spaceAfter=12))
    styles.add(ParagraphStyle(name='AnswerText', parent=styles['Normal'], spaceAfter=6, fontSize=9, leading=11))
    
    story = []
    
    # Section 1: Assessment
    story.append(Paragraph("Assessment", styles['Header1']))
    story.append(Spacer(1, 12))
    
    for q in questions:
        q_text = f"<b>{q['id']}.</b> {q['text']}"
        story.append(Paragraph(q_text, styles['QuestionText']))
        
        # Choices
        # Qualtrics choices don't have A) B) C) labels in the import file usually, 
        # but in my RoughText they did. In convert_to_qualtrics.py I stripped them?
        # Let's check convert_to_qualtrics.py...
        # "current_choices.append(choice_match.group(2))" -> Yes, I stripped "A) "
        # So I should re-add them for the PDF.
        labels = ['A', 'B', 'C', 'D', 'E', 'F']
        for i, choice in enumerate(q['choices']):
            label = labels[i] if i < len(labels) else "?"
            story.append(Paragraph(f"<b>{label})</b> {choice}", styles['ChoiceText']))
            
        story.append(Spacer(1, 12))
        
    # Section 2: Answer Key
    story.append(PageBreak())
    story.append(Paragraph("Answer Key", styles['Header1']))
    story.append(Spacer(1, 12))
    
    for q in questions:
        qid = q['id']
        if qid in answers:
            ans_data = answers[qid]
            text = f"<b>{qid}: {ans_data['answer']}</b><br/>{ans_data['rationale']}"
            story.append(Paragraph(text, styles['AnswerText']))
        else:
            story.append(Paragraph(f"<b>{qid}:</b> Answer not found", styles['AnswerText']))
            
    doc.build(story)
    print(f"Generated {output_file}")

if __name__ == "__main__":
    generate_pdf()
