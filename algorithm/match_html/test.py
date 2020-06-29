
def is_matched_html(html):
    s = []
    j = html.find('<')
    while j != -1:

        end = html.find('>', j+1)

        if end == -1:
            return False

        full_tag = html[j+1:end]

        blank = full_tag.find(' ')

        if blank == -1:
            tag = full_tag
        else:
            tag = full_tag[0:blank]


        print(full_tag)
        
        if tag[0] == '/':
            if len(s) == 0:

                return False
            if s.pop() != tag[1:]:

                return False
        
        elif tag[0] == '!':
            pass
        
        else:
            if full_tag[-1] != '/':
                if tag in ['input', 'img', 'link', 'meta', 'area']:
                    print(tag, "end should with '/'")
                else:
                    s.append(tag)
            else:
                
                if tag in ['input', 'img', 'link', 'meta', 'area']:
                    pass
                else:

                    return False
            
        j = html.find('<', end+1)
    return len(s) == 0



with open('1.html', encoding='utf-8') as fd:
    html=fd.read()
    r = is_matched_html(html)
    print(r)