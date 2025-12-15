from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import re

def generate_pdf():
    input_file = "RelationshipQuestions.md"
    output_file = "RelationshipAssessment.pdf"
    
    with open(input_file, 'r') as f:
        lines = f.readlines()
        
    # Parse content
    questions = []
    current_q = {}
    
    # Regex
    q_start_pattern = re.compile(r'^\*\*Q(\d+)\.\*\*\s*(.*)')
    choice_pattern = re.compile(r'^([A-D])\)\s*(.*)')
    answer_pattern = re.compile(r'^\*\*Answer:\s*([A-D])\*\*')
    rationale_pattern = re.compile(r'^\*Rationale:\s*(.*)\*')
    
    state = "LOOKING"
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        q_match = q_start_pattern.match(line)
        if q_match:
            if current_q:
                questions.append(current_q)
            current_q = {
                'id': f"Q{q_match.group(1)}",
                'text': q_match.group(2),
                'choices': [],
                'answer': '',
                'rationale': ''
            }
            state = "Q_TEXT"
            continue
            
        choice_match = choice_pattern.match(line)
        if choice_match:
            current_q['choices'].append(f"{choice_match.group(1)}) {choice_match.group(2)}")
            continue
            
        ans_match = answer_pattern.match(line)
        if ans_match:
            current_q['answer'] = ans_match.group(1)
            continue
            
        rat_match = rationale_pattern.match(line)
        if rat_match:
            current_q['rationale'] = rat_match.group(1)
            continue
            
        # Append text if in Q_TEXT state and not meta
        if state == "Q_TEXT" and not (line.startswith("**") or line.startswith("*") or line.startswith("#") or line.startswith("---")):
            current_q['text'] += " " + line

    if current_q:
        questions.append(current_q)
        
    # Generate PDF
    doc = BaseDocTemplate(output_file, pagesize=letter)
    
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
    story.append(Paragraph("Relationship Skills Assessment", styles['Header1']))
    story.append(Spacer(1, 12))
    
    for q in questions:
        q_text = f"<b>{q['id']}.</b> {q['text']}"
        story.append(Paragraph(q_text, styles['QuestionText']))
        for choice in q['choices']:
            story.append(Paragraph(f"<b>{choice.split(')')[0]})</b> {choice.split(')')[1]}", styles['ChoiceText']))
        story.append(Spacer(1, 12))
        
    # Section 2: Answer Key
    story.append(PageBreak())
    story.append(Paragraph("Answer Key", styles['Header1']))
    story.append(Spacer(1, 12))
    
    for q in questions:
        text = f"<b>{q['id']}: {q['answer']}</b><br/>{q['rationale']}"
        story.append(Paragraph(text, styles['AnswerText']))
        
    doc.build(story)
    print(f"Generated {output_file}")

if __name__ == "__main__":
    generate_pdf()
