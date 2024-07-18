import py_docx_cc

template_file = "../docx-cc/tests/data/content_controlled_document.docx"

with open(template_file, "rb") as f:
    data = f.read()

mappings = {
    "Title": "Nothing else matters",
}

print(py_docx_cc.get_content_controls(data))
mapped_result = py_docx_cc.map_content_controls(data, mappings)

result_file = "yes.docx"

with open(result_file, "wb") as f:
    f.write(mapped_result)
