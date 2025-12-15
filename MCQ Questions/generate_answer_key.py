import re

def generate_answer_key():
    input_file = "RoughText.md"
    output_file = "AnswerKey.md"
    
    with open(input_file, 'r') as f:
        lines = f.readlines()
        
    key_lines = []
    key_lines.append("| Question ID | Correct Answer | Rationale |\n")
    key_lines.append("|---|---|---|\n")
    
    current_q_id = None
    current_answer = None
    current_rationale = None
    
    q_pattern = re.compile(r'^Q(\d+)\.')
    
    for line in lines:
        line = line.strip()
        
        # Check for Question ID
        match = q_pattern.match(line)
        if match:
            # Save previous if exists
            if current_q_id and current_answer:
                # Clean rationale if it exists
                rat = current_rationale if current_rationale else ""
                key_lines.append(f"| {current_q_id} | {current_answer} | {rat} |\n")
            
            current_q_id = f"Q{match.group(1)}"
            current_answer = None
            current_rationale = None
            continue
            
        # Check for Answer
        if line.startswith("Answer:"):
            current_answer = line.replace("Answer:", "").strip()
            
        # Check for Rationale
        if line.startswith("Rationale:"):
            current_rationale = line.replace("Rationale:", "").strip()
            
    # Save last one
    if current_q_id and current_answer:
        rat = current_rationale if current_rationale else ""
        key_lines.append(f"| {current_q_id} | {current_answer} | {rat} |\n")
        
    with open(output_file, 'w') as f:
        f.writelines(key_lines)
        
    print(f"Generated {output_file}")

if __name__ == "__main__":
    generate_answer_key()
