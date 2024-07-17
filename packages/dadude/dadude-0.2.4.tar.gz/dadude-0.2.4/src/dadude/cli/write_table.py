from functools import partial
from fire import Fire
from ..writer.delta_writer import write_json_table, overwrite_json_table


write_property_entity_v3 = partial(
    write_json_table,
    local_json_file_path="data/gold/material_property_entity_v3.json",
)

write_dc_annotation_spum_cn_clms_2407 = partial(
    write_json_table,
    lines=True,
    local_json_file_path="data/bronze/dc_annotation_spum_cn_clms_2407.json",
)

overwrite_dc_annotation_spum_cn_clms_2407 = partial(
    overwrite_json_table,
    lines=True,
    local_json_file_path="data/bronze/dc_annotation_spum_cn_clms_2407.json",
)

if __name__ == "__main__":
    Fire()
