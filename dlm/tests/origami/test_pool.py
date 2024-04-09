from dlm.origami.pool import Pool
import pytest
import os

input_dir = os.path.join('dlm', 'tests', 'origami', 'input_jsons')
json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]

@pytest.mark.parametrize("json_file", json_files)
def test_write_top(json_file):
    pool_name = os.path.splitext(json_file)[0]
    json_path = os.path.join(input_dir, json_file)
    pool = Pool(json_path)

    expected_path = os.path.join('dlm', 'tests', 'origami','expected_output','Topology',pool_name+'.top')
    generated_path = 'temp.top'

    pool.write_top_Oct19(generated_path)
    with open(generated_path, 'r') as file:
        generated_content = file.read()
    with open(expected_path, 'r') as file:
        expected_content = file.read()

    os.remove(generated_path)

    assert generated_content == expected_content, f"The generated topology file for {pool_name} does not match the expected output."

@pytest.mark.parametrize("json_file", json_files)
def test_write_ops(json_file):
    pool_name = os.path.splitext(json_file)[0]
    json_path = os.path.join(input_dir, json_file)
    pool = Pool(json_path)

    expected_path = os.path.join('dlm', 'tests', 'origami','expected_output','OPs',pool_name+'_OP.txt')
    generated_path = pool_name+'_OP.txt'

    pool.write_OP_Oct19('',pool_name)
    with open(generated_path, 'r') as file:
        generated_content = file.read()
    with open(expected_path, 'r') as file:
        expected_content = file.read()

    os.remove(generated_path)

    assert generated_content == expected_content, f"The generated order parameter file for {pool_name} does not match the expected output."

