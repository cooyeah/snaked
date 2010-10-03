import gtk
import pango

def editor_opened(editor):
    editor.connect('file-saved', on_file_saved)
    on_file_saved(editor)
    
def editor_closed(editor):
    pass
    
def on_file_saved(editor):
    try:
        problems = get_problem_list(editor.uri)
    except Exception, e:
        editor.message(str(e), 5000)
        return

    mark_problems(editor, problems)

def get_tag(editor):
    table = editor.buffer.get_tag_table()
    tag = table.lookup('flakes')
    if not tag:
        tag = editor.buffer.create_tag('flakes', underline=pango.UNDERLINE_ERROR)
    
    return tag

def mark_problems(editor, problems):
    start, end = editor.buffer.get_bounds()
    
    if editor.buffer.get_tag_table().lookup('flakes'):
        editor.buffer.remove_tag_by_name('flakes', start, end)
    
    for line, name, message in problems:
        iter = editor.buffer.get_iter_at_line(line-1)
        nstart, nend = iter.forward_search(name, gtk.TEXT_SEARCH_VISIBLE_ONLY)
        editor.buffer.apply_tag(get_tag(editor), nstart, nend) 
        
def get_problem_list(filename):
    import subprocess
    import re
    
    stdout, stderr = subprocess.Popen(['/usr/bin/env', 'pyflakes', filename],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

    if stderr:
        raise Exception('python_flakes plugin: ' + stderr)
    
    result = []
    match_name = re.compile(r"'(.*?)'")
    for m in re.finditer(r"(?m)^.*?:(?P<line>\d+):\s*(?P<message>.*$)", stdout):
        line, message = m.group('line', 'message')
        name = match_name.search(message)
        if not name:
            raise Exception("Can't parse variable name in " + message)
        
        result.append((int(line), name.group(1), message))
        
    return result