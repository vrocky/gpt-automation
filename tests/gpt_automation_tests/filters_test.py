from gpt_automation.filters import should_include_by_include_only_list

def test_should_include_by_include_only_list_with_no_active_rules():
    include_only_matches_stack = [None, None, None]
    file_path = '.\\captcha_decoder\\decode.py'
    assert should_include_by_include_only_list(file_path, include_only_matches_stack) == True

def test_should_include_by_include_only_list_with_active_rules_and_matching_path():
    include_only_matches_stack = [None, [('.', '*captcha_decoder*'), ('.', '*tests*')], None]
    file_path = '.\\captcha_decoder\\decode.py'
    assert should_include_by_include_only_list(file_path, include_only_matches_stack) == True

def test_should_include_by_include_only_list_with_active_rules_and_non_matching_path():
    include_only_matches_stack = [None, [('.', '*captcha_decoder*'), ('.', '*tests*')], None]
    file_path = '.\\non_matching_folder\\file.py'
    assert should_include_by_include_only_list(file_path, include_only_matches_stack) == False
