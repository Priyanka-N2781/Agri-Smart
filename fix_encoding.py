import os
html_files = [f for f in os.listdir('.') if f.endswith('.html')]
for file in html_files:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        content = content.replace('â€”', '&mdash;')
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f'Error on {file}: {e}')
