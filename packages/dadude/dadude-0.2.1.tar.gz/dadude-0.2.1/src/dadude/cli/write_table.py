from functools import partial
from fire import Fire
from ..writer.delta_writer import write_json_table


write_property_entity_v3 = partial(
    write_json_table, local_json_file_path="data/gold/material_property_entity_v3.json"
)


if __name__ == "__main__":
    Fire(write_json_table)
