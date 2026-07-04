def test_loader_row_count(generator):
    assert generator.row_count == 30


def test_loader_parquet_readable(generator):
    assert generator.count_filtered() == 30
