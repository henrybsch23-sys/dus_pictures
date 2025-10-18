"""Export notebook to simple HTML (without nbconvert templates)"""
import nbformat
import html as html_module

# Read notebook
print("Reading dicom_to_ts.ipynb...")
nb = nbformat.read('dicom_to_ts.ipynb', as_version=4)

# Build simple HTML
print("Converting to HTML...")
html_parts = ['''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Doppler Ultrasound Time-Series Extraction</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 40px auto; padding: 20px; background: #f5f5f5; }
        .cell { background: white; margin: 20px 0; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .markdown { line-height: 1.6; }
        .markdown h1 { color: #333; border-bottom: 2px solid #333; padding-bottom: 10px; }
        .markdown h2 { color: #555; margin-top: 30px; }
        .markdown code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; }
        .markdown pre { background: #f8f8f8; padding: 15px; border-left: 3px solid #333; overflow-x: auto; }
        .output { background: #f9f9f9; border-left: 3px solid #4CAF50; padding: 15px; margin-top: 10px; }
        .output pre { margin: 0; }
        img { max-width: 100%; height: auto; }
    </style>
</head>
<body>
''']

for cell in nb['cells']:
    if cell['cell_type'] == 'markdown':
        # Simple markdown to HTML conversion
        content = ''.join(cell['source'])
        content = html_module.escape(content)
        # Basic markdown replacements
        content = content.replace('\\n## ', '</p><h2>').replace('\\n# ', '</p><h1>')
        content = content.replace('## ', '<h2>').replace('# ', '<h1>')
        content = content.replace('</h1>', '</h1><p>').replace('</h2>', '</h2><p>')
        content = content.replace('- **', '<br>• <strong>').replace('**:', '</strong>:')
        content = content.replace('**', '</strong>').replace('<strong></strong>', '<strong>')
        html_parts.append(f'<div class="cell markdown">{content}</p></div>')
    
    elif cell['cell_type'] == 'code':
        # Only show outputs, not code (exclude_input=True)
        if 'outputs' in cell and cell['outputs']:
            html_parts.append('<div class="cell">')
            for output in cell['outputs']:
                if output['output_type'] == 'stream':
                    text = ''.join(output['text'])
                    html_parts.append(f'<div class="output"><pre>{html_module.escape(text)}</pre></div>')
                elif output['output_type'] == 'execute_result' or output['output_type'] == 'display_data':
                    if 'data' in output and 'text/plain' in output['data']:
                        text = ''.join(output['data']['text/plain'])
                        html_parts.append(f'<div class="output"><pre>{html_module.escape(text)}</pre></div>')
                    if 'data' in output and 'image/png' in output['data']:
                        img_data = output['data']['image/png']
                        html_parts.append(f'<div class="output"><img src="data:image/png;base64,{img_data}"/></div>')
            html_parts.append('</div>')

html_parts.append('</body></html>')
html = ''.join(html_parts)

# Save
print("Saving output/dicom_to_ts.html...")
with open('output/dicom_to_ts.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("SUCCESS: Created output/dicom_to_ts.html")
print("Open output/dicom_to_ts.html in your web browser to view it.")

