import re

# number of characters for too long token
TOKEN_TO_LONG = 30


def fix_html(t, cut_long=False):
    """
    cut_long = if True then cuts long tokens to fixed number defined by TOKEN_TO_LONG
    """
    if t is None:
        return ''

    if cut_long:
        tokens = re.split(r"\s+", t)
        split_tokens = []
        for tok in tokens:
            if len(tok) > TOKEN_TO_LONG:
                tok = tok[:TOKEN_TO_LONG] + '[...]'
            split_tokens.append(tok)
        t = " ".join(split_tokens)
    re.sub("[<>/]+", " ", t)
    return t


def surround_tag(tag, text):
    return f"<{tag}>{text}</{tag}>"


def create_html_link_string(url, link_text=None, new_tab=True):
    result = '<a href="' + url + '"'
    if new_tab:
        result += 'target="__blank__"'
    result += ">"
    if link_text:
        result += link_text
    else:
        result += url
    result += "</a>"
    return result


def create_html_table_string(table_data, with_border=True, cellpadding=5, cellspacing=5, table_align=None, table_width=None, col_align=None,
                                 add_bg_for_odd_rows=False, add_bg_for_even_rows=False, header_bg_color=None):
    """
    Generates HTML of the table data.
    add_bg_for_odd_rows: if set to RGB color (e.g. #AABBCC then odd rows will have different bg color)
    add_bg_for_even_rows: if set to RGB color (e.g. #AABBCC then even rows will have different bg color)
    header_bg_color: if set to RGB color then header will have different bg color
    """
    result_rows = []

    first_row = "<table"
    if with_border:
        first_row += ' border="1"'
    if cellpadding > 0:
        first_row += ' cellpadding="' + str(cellpadding) + '"'
    if cellspacing > 0:
        first_row += ' cellspacing="' + str(cellspacing) + '"'
    if table_align:
        first_row += ' align="' + table_align + '"'
    if table_width:
        first_row += ' width="' + table_width + '"'
    first_row += ">"

    result_rows.append(first_row)
    for i, row in enumerate(table_data):
        tr_text = "<tr "
        if i == 0:
            if header_bg_color:
                tr_text += ' bgcolor="' + header_bg_color + '"'

        if i % 2 == 0:
            if add_bg_for_odd_rows:
                if not 'bgcolor' in tr_text:
                    tr_text += ' bgcolor="' + add_bg_for_odd_rows + '"'
        if i % 2 == 1:
            if add_bg_for_even_rows:
                if not 'bgcolor' in tr_text:
                    tr_text += ' bgcolor="' + add_bg_for_even_rows + '"'
        tr_text += ">"
        result_rows.append(tr_text)
        for i, e in enumerate(row):
            td_txt = "<td"
            if col_align:
                if i < len(col_align):
                    td_txt += ' align="' + col_align[i] + '"'
            td_txt += '>'

            result_rows.append(td_txt)
            result_rows.append(str(e))
            result_rows.append("</td>")
        result_rows.append("</tr>")
    result_rows.append("</table>")
    return "\n".join(result_rows)


def create_interactive_html_table_string(
        table_data,
        header_data,
        table_name,
        with_pagination=False,
        with_toggle_columns=True,
        with_search_in_each_column=True,
        add_index=False,
        ):
    """
    This will create HTML table with sortable and interactive options
    It will use: https://datatables.net

    If you want to use it then you will need to add the following links in the page header:

    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.25/css/jquery.dataTables.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js"></script>
    <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.10.25/js/jquery.dataTables.js"></script>

    And also styles:
<style>
tfoot input {
        width: 100%;
        padding: 3px;
        box-sizing: border-box;
    }
</style>

    """

    result_rows = []
    if with_toggle_columns:
        result_rows.append("<p>Widoczność kolumny (kliknij aby pokazać lub ukryć):")
        for index, col_name in enumerate(header_data):
            sep = ''
            if index > 0:
                sep = ' --- '
            result_rows.append(sep + '<a class="toggle-vis" data-column="' + str(index) + '"><b>[[' + col_name + ']]</b></a>')
        result_rows.append("</p>")

    result_rows.append(f'<table id={table_name} class="display" style="width:100%">')

    result_rows.append("<thead>")
    result_rows.append("<tr>")

    if add_index:
        result_rows.append(f"<th>Id</th>")

    for cell in header_data:
        result_rows.append(f"<th>{cell}</th>")
    result_rows.append("</tr>")
    result_rows.append("</thead>")

    result_rows.append("<tbody>")
    i = 0
    for row_data in table_data:
        i += 1
        result_rows.append("<tr>")
        if add_index:
            result_rows.append(f"<td>{i}</td>")

        for cell in row_data:
            result_rows.append(f"<td>{cell}</td>")
        result_rows.append("</tr>")

    result_rows.append("</tbody>")

    if with_search_in_each_column:
        result_rows.append("<tfoot>")
        result_rows.append("<tr>")
        for cell in header_data:
            result_rows.append(f"<th>{cell}</th>")
        result_rows.append("</tr>")
        result_rows.append("</tfoot>")
    result_rows.append('</table>')

    result_rows.append('<script>')
    result_rows.append('$(document).ready(function () {')

    if with_search_in_each_column:
        result_rows.append(f"$('#{table_name} tfoot th').each( function ()" + " {")
        result_rows.append("""
        var title = $(this).text();
        $(this).html( '<input type="text" placeholder="? '+title+'" />' );
    } );
        """)

    result_rows.append(f"    var table = $('#{table_name}').DataTable(" + "{")
    result_rows.append(f'          "paging":   {str(with_pagination).lower()},')
    result_rows.append(f'          "pageLength": 1000,')
    result_rows.append( '          "info":   true,')

    if with_search_in_each_column:
        result_rows.append("""
            initComplete: function () {
                // Apply the search
                this.api().columns().every( function () {
                    var that = this;
                    $( 'input', this.footer() ).on( 'keyup change clear', function () {
                        if ( that.search() !== this.value ) {
                            that
                                .search( this.value )
                                .draw();
                        }
                    } );
                } );
            }
        """)

    result_rows.append( '    });')
    if with_toggle_columns:
        result_rows.append("$('a.toggle-vis').on( 'click', function (e) {")
        result_rows.append("e.preventDefault();")
        result_rows.append("var column = table.column( $(this).attr('data-column') );")
        result_rows.append("column.visible( ! column.visible() );")
        result_rows.append('});')
    result_rows.append('});')

    result_rows.append('</script>')

    return "\n".join(result_rows)


def write_report_header(f, report_name, prev_report_id):
    f.write(f"""
<html>
<head>
<title>{report_name}</title>
<meta charset="UTF-8">
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.25/css/jquery.dataTables.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js"></script>
    <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.10.25/js/jquery.dataTables.js"></script>
""")
    f.write("""
<style>
tfoot input {
        width: 100%;
        padding: 3px;
        box-sizing: border-box;
    }
</style>
</head>

""")
    f.write(f"""
<body>
<p>
Aby powrócić do głównego raportu kliknij: <a href="{prev_report_id}">{prev_report_id}</a>
</p>
""")


def write_report_bottom(f, prev_report_id):
    f.write(f"""
<p>
Aby powrócić do głównego raportu kliknij: <a href="{prev_report_id}">{prev_report_id}</a>
</p>
</body>
</html>
""")
