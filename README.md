# python-quill-delta

[![Build Status](https://travis-ci.org/mariocesar/python-quill-delta.svg?branch=master)](https://travis-ci.org/mariocesar/python-quill-delta)

Implements all quill-delta operations in Python. 

Also implements:

- [ ] Delta to HTML
- [ ] Delta to Plain Text
- [ ] Delta to PDF

!!NOTE This is early work, is not 100% usable


## Test Progress

    collected 37 items                                                                                         
    
    tests/test_builder.py::TestConstructor::test_empty PASSED                                            [  2%]
    tests/test_builder.py::TestConstructor::test_empty_ops PASSED                                        [  5%]
    tests/test_builder.py::TestConstructor::test_array_of_ops PASSED                                     [  8%]
    tests/test_builder.py::TestConstructor::test_delta_in_object_form PASSED                             [ 10%]
    tests/test_builder.py::TestConstructor::test_delta PASSED                                            [ 13%]
    tests/test_builder.py::TestInsert::test_insert_text PASSED                                           [ 16%]
    tests/test_builder.py::TestInsert::test_insert_text_none PASSED                                      [ 18%]
    tests/test_builder.py::TestInsert::test_insert_embed PASSED                                          [ 21%]
    tests/test_builder.py::TestInsert::test_insert_embed_attributes PASSED                               [ 24%]
    tests/test_builder.py::TestInsert::test_insert_embed_non_integer PASSED                              [ 27%]
    tests/test_builder.py::TestInsert::test_insert_text_attributes PASSED                                [ 29%]
    tests/test_builder.py::TestInsert::test_insert_text_after_delete PASSED                              [ 32%]
    tests/test_builder.py::TestInsert::test_insert_text_after_delete_with_merge PASSED                   [ 35%]
    tests/test_builder.py::TestInsert::test_insert_text_after_delete_no_merge PASSED                     [ 37%]
    tests/test_builder.py::TestInsert::test_insert_text_empty_attributes PASSED                          [ 40%]
    tests/test_builder.py::TestInsert::test_delta_insert_text PASSED                                     [ 43%]
    tests/test_builder.py::TestDelete::test_delete_0 PASSED                                              [ 45%]
    tests/test_builder.py::TestDelete::test_delete_positive PASSED                                       [ 48%]
    tests/test_builder.py::TestDelete::test_delta_delete_text PASSED                                     [ 51%]
    tests/test_builder.py::TestRetain::test_retain_0 PASSED                                              [ 54%]
    tests/test_builder.py::TestRetain::test_retain_length PASSED                                         [ 56%]
    tests/test_builder.py::TestRetain::test_retain_length_none PASSED                                    [ 59%]
    tests/test_builder.py::TestRetain::test_retain_length_attributes PASSED                              [ 62%]
    tests/test_builder.py::TestRetain::test_retain_length_empty_attributes PASSED                        [ 64%]
    tests/test_builder.py::TestPush::test_push_into_empty PASSED                                         [ 67%]
    tests/test_builder.py::TestPush::test_push_consecutive_delete PASSED                                 [ 70%]
    tests/test_builder.py::TestPush::test_push_consecutive_text PASSED                                   [ 72%]
    tests/test_builder.py::TestPush::test_push_consecutive_text_with_matching_attributes PASSED          [ 75%]
    tests/test_builder.py::TestPush::test_push_consecutive_retain_with_matching_attributes PASSED        [ 78%]
    tests/test_builder.py::TestPush::test_push_consecutive_text_with_not_matching_attributes PASSED      [ 81%]
    tests/test_builder.py::TestPush::test_push_consecutive_retain_with_not_matching_attributes PASSED    [ 83%]
    tests/test_builder.py::TestPush::test_push_consecutive_embeds_with_matching_attributes PASSED        [ 86%]
    tests/test_delta.py::TestCompose::test_insert_insert PASSED                                          [ 89%]
    tests/test_delta.py::TestCompose::test_insert_retain PASSED                                          [ 91%]
    tests/test_delta.py::TestCompose::test_insert_delete PASSED                                          [ 94%]
    tests/test_delta.py::TestCompose::test_delete_insert PASSED                                          [ 97%]
    tests/test_delta.py::TestCompose::test_delete_retain PASSED                                          [100%]
