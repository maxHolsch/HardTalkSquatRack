import re

def convert_to_qualtrics():
    input_file = "RelationshipQuestions.md"
    output_file = "RelationshipQuestions_Qualtrics.txt"
    
    with open(input_file, 'r') as f:
        lines = f.readlines()
        
    qualtrics_lines = []
    qualtrics_lines.append("[[AdvancedFormat]]\n\n")
    
    current_q_id = None
    current_q_text = []
    current_choices = []
    
    # Regex patterns
    # Matches "**Q1.** Question text" or "**Q1.**" and text on next line?
    # File has: "**Q1.** Your neighbor..."
    q_start_pattern = re.compile(r'^\*\*Q(\d+)\.\*\*\s*(.*)')
    
    # Choices: "A) ..."
    choice_pattern = re.compile(r'^([A-D])\)\s*(.*)')
    
    state = "LOOKING_FOR_Q"
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for start of a new question
        q_match = q_start_pattern.match(line)
        if q_match:
            # Save previous
            if current_q_id:
                save_question(qualtrics_lines, current_q_id, current_q_text, current_choices)
                current_q_text = []
                current_choices = []
            
            current_q_id = f"Q{q_match.group(1)}"
            text_part = q_match.group(2)
            if text_part:
                current_q_text.append(text_part)
            state = "READING_Q"
            continue
            
        # Check for choices
        choice_match = choice_pattern.match(line)
        if choice_match:
            state = "READING_CHOICES"
            current_choices.append(choice_match.group(2))
            continue
            
        # Handle other lines
        if state == "READING_Q":
            # Ignore meta lines
            if is_meta_line(line):
                continue
            current_q_text.append(line)
            
        elif state == "READING_CHOICES":
            if is_meta_line(line):
                continue
            # Could be continuation of a choice? 
            # In this file, choices seem to be single paragraphs.
            pass
            
    # Save last
    if current_q_id:
        save_question(qualtrics_lines, current_q_id, current_q_text, current_choices)
        
    with open(output_file, 'w') as f:
        f.writelines(qualtrics_lines)
        
    print(f"Converted to {output_file}")

def is_meta_line(line):
    # Ignore headers, separators, answer keys
    if line.startswith("**Answer:") or line.startswith("*Rationale:") or line.startswith("**Difficulty:"):
        return True
    if line.startswith("---") or line.startswith("##") or line.startswith("# "):
        return True
    if line.startswith("### Type"):
        return True
    return False

def save_question(lines, q_id, q_text_list, choices):
    lines.append("[[Question:MC]]\n")
    lines.append(f"[[ID:{q_id}]]\n")
    
    full_text = " ".join(q_text_list)
    lines.append(f"{full_text}\n")
    
    lines.append("[[Choices]]\n")
    for choice in choices:
        lines.append(f"{choice}\n")
    
    lines.append("\n")

if __name__ == "__main__":
    convert_to_qualtrics()
