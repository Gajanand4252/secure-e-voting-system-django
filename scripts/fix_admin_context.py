p = r'EC_Admin\views.py'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()
old1 = "get_admin_context(request)\\['username'\\]"
old2 = "get_admin_context(request)\\['image'\\]"
s = s.replace(old1, "get_admin_context(request)['username']")
s = s.replace(old2, "get_admin_context(request)['image']")
with open(p, 'w', encoding='utf-8') as f:
    f.write(s)
print('done')
