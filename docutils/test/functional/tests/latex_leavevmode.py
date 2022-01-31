settings_overrides = {
    # disable configuration files
    '_disable_config': True,
    # Default settings for all tests.
    'report_level': 2,
    'halt_level': 5,
    'warning_stream': False,
    'input_encoding': 'utf-8',
    'embed_stylesheet': False,
    'auto_id_prefix': '%',
    # avoid "Pygments not found"
    'syntax_highlight': 'none'
}
# Source and destination file names.
test_source = "latex_leavevmode.txt"
test_destination = "latex_leavevmode.tex"

# Keyword parameters passed to publish_file.
writer_name = "latex"

# Settings
# use "smartquotes" transition:
settings_overrides['smart_quotes'] = True
settings_overrides['legacy_column_widths'] = True
settings_overrides['use_latex_citations'] = False
