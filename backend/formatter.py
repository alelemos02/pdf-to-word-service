import re
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import RGBColor

def clean_and_format_docx(input_path: str, output_path: str):
    doc = Document(input_path)
    
    # 1. Setup Standard Styles (Heuristic)
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)
    
    # Regex for detecting lists
    # Matches "1.", "1.1", "1.1.1", "a)", "a.", "- ", "• "
    numbering_regex = re.compile(r'^\s*(\d+(\.\d+)*\.?|[a-z]\)|\-)\s+')
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
            
        # Remove weird double spaces
        para.text = re.sub(r'\s+', ' ', text)
        
        # 2. Check for Headings (Heuristic: All Caps + Short or Bold)
        # Attempt to detect if it looks like a title
        if (len(text) < 100 and text.isupper()) or (len(text) < 50 and para.runs and para.runs[0].bold):
             # You might want to apply a Heading style, but be careful not to break things.
             # For now, let's just ensure it has space before/after
             para_format = para.paragraph_format
             para_format.space_before = Pt(12)
             para_format.space_after = Pt(6)
             continue

        # 3. List Detection
        match = numbering_regex.match(text)
        if match:
             # It looks like a list item!
             # We can't easily convert to "real" Word lists without XML manipulation (complex),
             # but we can simulate the indentation which is usually what's broken.
             
             # Calculate indentation level based on dots in numbering (e.g. 1.1.1 is level 2)
             marker = match.group(1)
             if marker in ['-', '•']:
                 level = 0
             else:
                 level = marker.count('.')
                 if marker.endswith('.'): level -= 1 # 1. is level 0
                 if level < 0: level = 0
             
             para_format = para.paragraph_format
             para_format.left_indent = Inches(0.25 + (level * 0.25))
             para_format.first_line_indent = Inches(-0.25) # Hanging indent
        else:
            # Standard Paragraph
            para_format = para.paragraph_format
            para_format.line_spacing = 1.15
            para_format.space_after = Pt(6)
            para_format.left_indent = Inches(0)
            para_format.first_line_indent = Inches(0)
            # Justify is often nice for formal docs, but Left is safer
            para.alignment = WD_ALIGN_PARAGRAPH.LEFT

    doc.save(output_path)
