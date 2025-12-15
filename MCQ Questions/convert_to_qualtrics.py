import re

def convert_to_qualtrics():
    input_file = "RoughText.md"
    output_file = "QualtricsImport.txt"
    
    with open(input_file, 'r') as f:
        lines = f.readlines()
        
    qualtrics_lines = []
    qualtrics_lines.append("[[AdvancedFormat]]\n\n")
    
    current_q_id = None
    current_q_text = []
    current_choices = []
    
    # Regex patterns
    q_start_pattern = re.compile(r'^Q(\d+)\.\s*(.*)')
    choice_pattern = re.compile(r'^([A-D])\)\s*(.*)')
    
    # We need to handle multi-line question text.
    # State machine: 
    # - LOOKING_FOR_Q: waiting for Qxx.
    # - READING_Q: reading question text lines until we hit a choice or empty line? 
    #   Actually choices usually start with A).
    # - READING_CHOICES: reading A), B), C), D).
    
    state = "LOOKING_FOR_Q"
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for start of a new question
        q_match = q_start_pattern.match(line)
        if q_match:
            # If we were processing a previous question, save it
            if current_q_id:
                save_question(qualtrics_lines, current_q_id, current_q_text, current_choices)
                current_q_text = []
                current_choices = []
            
            current_q_id = f"Q{q_match.group(1)}"
            current_q_text.append(q_match.group(2))
            state = "READING_Q"
            continue
            
        # Check for choices
        choice_match = choice_pattern.match(line)
        if choice_match:
            # If we find a choice, we are definitely in READING_CHOICES or transitioning to it
            state = "READING_CHOICES"
            current_choices.append(choice_match.group(2))
            continue
            
        # Handle other lines based on state
        if state == "READING_Q":
            # If it's not a choice and not a new question, append to question text
            # But we need to be careful about "Answer:", "Rationale:", "Difficulty:", "Type A:", "SKILL 1:"
            if is_meta_line(line):
                continue
            current_q_text.append(line)
            
        elif state == "READING_CHOICES":
            # If we are reading choices, and we see a non-choice line
            # It might be a multiline choice (unlikely in this format) or meta info
            if is_meta_line(line):
                continue
            # If it's just text, it might be continuation of previous choice?
            # For this specific file, choices seem to be single line.
            # Let's assume meta lines end the question block effectively.
            pass

    # Save the last question
    if current_q_id:
        save_question(qualtrics_lines, current_q_id, current_q_text, current_choices)
        
    with open(output_file, 'w') as f:
        f.writelines(qualtrics_lines)
        
    print(f"Converted to {output_file}")

def is_meta_line(line):
    meta_prefixes = ["Answer:", "Rationale:", "Difficulty:", "Type ", "SKILL ", "Context:"]
    # Wait, "Context:" is part of the question text usually!
    # The file has "Qxx. Context: ..."
    # But sometimes "Context:" is on a new line?
    # Let's check the file content again.
    # Line 801: Q75. Context: A customer service escalation:
    # Line 802: Customer: "..."
    # So "Context:" is part of the question.
    
    # "Type A:", "SKILL 1:" are headers we want to ignore or include?
    # User said "remove all of the duplicate questions, as well as the prompt information".
    # "Type A: ..." and "SKILL 1: ..." look like prompt info / headers.
    
    if line.startswith("Answer:") or line.startswith("Rationale:") or line.startswith("Difficulty:"):
        return True
    if line.startswith("Type ") or line.startswith("SKILL "):
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
