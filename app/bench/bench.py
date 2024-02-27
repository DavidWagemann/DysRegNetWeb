from ..pages.components.user_input import prepare_control_data
import json
import cProfile

if __name__ == "__main__":
    expression = json.load(open("app/bench/expression_dict.txt"))
    control_option = "gene_tpm_bladder.gct"

    with cProfile.Profile() as pr:
        prepare_control_data(control_option, expression)
        pr.print_stats()