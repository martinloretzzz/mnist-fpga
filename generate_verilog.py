import json
import math

def chunk_list(arr, chunk_size):
    return [arr[i:i + chunk_size] for i in range(0, len(arr), chunk_size)]


def extract_tree(node, parents=None):
    if parents is None: 
        parents = []
    assert isinstance(node, dict)
    if "leaf" in node:
        return [(parents, node["leaf"])]
    if "children" in node:
        left_parents = [*parents, node["split"].replace("f", "n")]
        right_parents = [*parents, node["split"].replace("f", "p")]
        return [*extract_tree(node["children"][0], left_parents),
                *extract_tree(node["children"][1], right_parents)]


def group_trees_by_classifier(trees, num_classes=10):
    classifiers = {}
    for tree_id, tree in enumerate(trees):
        classifier_id = tree_id % num_classes
        classifiers.setdefault(classifier_id, [])
        classifiers[classifier_id].append(tree)
    return classifiers


def generate_decision_tree_module(classifiers):  
    def get_classifier_module(classifier_id, classifier_trees):
        leaf_id = 0
        statements = []
        for iteration_id, tree in enumerate(classifier_trees):
            statements.append(f"// Classifier: {classifier_id} Iteration: {iteration_id}")
            for leaf, value in tree:
                statement = f"assign leaf[{leaf_id}] = {" && ".join([f"{"!" if term.startswith("n") else ""}f[{term[1:]}]" for term in leaf])};"
                statements.append(statement)
                leaf_id += 1
            statements.append("")
        leaf_count = leaf_id
        return f"""
module decision_tree_leaves_{classifier_id}(input logic [0:{28*28-1}] f, output logic [0:{leaf_count-1}] leaf);
\t{"\n\t".join(statements)}
endmodule
"""

    return "\n\n\n".join([get_classifier_module(classifier_id, classifier_trees) for classifier_id, classifier_trees in classifiers.items()])


def generate_leaf_counter_module(classifiers):  
    discrete_values = [-0.25, -0.125, -0.0625, -0.03125, -0.015625, 0.015625, 0.03125, 0.0625, 0.125, 0.25, 0.5, 1.0, 2.0]

    def get_classifier_module(classifier_id, classifier_trees):
        leaf_id = 0
        leaf_ids_by_value = {}
        for tree in classifier_trees:
            leaf_ids_by_value_in_tree = {}
            for leaf, value in tree:
                leaf_ids_by_value_in_tree.setdefault(value, [])
                leaf_ids_by_value_in_tree[value].append(leaf_id)
                leaf_id += 1

            for value, leaf_id_group in leaf_ids_by_value_in_tree.items():
                leaf_ids_by_value.setdefault(value, [])
                leaf_ids_by_value[value].append(leaf_id_group)

        def combine_leaf_groups(leaf_groups):
            return [" || ".join([f"l[{str(leaf_id)}]" for leaf_id in leaf_group]) for leaf_group in leaf_groups]

        def generate_leaf_prefix_summer(value_id, terms):
            first_layer_group_size=4
            reduce_depth_count=5

            buf_prefix = f"v{value_id}c{classifier_id}"
            def buf(depth, i, postfix=""):
                return f"{buf_prefix}l{depth}{postfix}[{i}]"

            assert len(terms) // first_layer_group_size < 2 ** reduce_depth_count

            terms = chunk_list(terms, first_layer_group_size)
            terms = [" + ".join(sum_group) for sum_group in terms]

            statements = []
            statements.append(f"logic [2:0] {buf_prefix}l{0}_out [0:{len(terms)-1}];")
            statements.append(f"logic [2:0] {buf_prefix}l{0} [0:{len(terms)-1}];")
            for i, term in enumerate(terms):
                statements.append(f"assign {buf_prefix}l{0}_out[{i}] = {term};")

            statements.append(f"""
    always_ff @(posedge clk) begin
        for (i = 0; i < {len(terms)}; i = i + 1)
            {buf_prefix}l{0}[i] <= {buf_prefix}l{0}_out[i];
    end\n""")

            term_count = len(terms)
            for layer_i in range(1, reduce_depth_count+1):
                next_term_count = math.ceil(term_count / 2)
                statements.append(f"reg [{2+layer_i}:0] {buf_prefix}l{layer_i} [0:{next_term_count-1}];")
                statements.append(f"logic [{2+layer_i}:0] {buf_prefix}l{layer_i}_out [0:{next_term_count-1}];")
                if term_count >= 2:
                    for i in range(next_term_count):
                        buf_name = buf(layer_i, i, postfix="_out")
                        if (2 * i + 1) < term_count:
                            statements.append(f"assign {buf_name} = {buf(layer_i-1, 2 * i)} + {buf(layer_i-1, 2 * i + 1)};")
                        else:
                            statements.append(f"assign {buf_name} = {buf(layer_i-1, 2 * i)};")
                else:
                    statements.append(f"assign {buf(layer_i, i, postfix="_out")} = {buf(layer_i-1, i)};")
                statements.append(f"""
    always_ff @(posedge clk) begin
        for (i = 0; i < {next_term_count}; i = i + 1)
            {buf(layer_i, "i")} <= {buf(layer_i, "i", postfix="_out")};
    end\n""")
                term_count = next_term_count

            statements.append(f"assign val[{value_id}] = {buf(layer_i, i)};")
            return statements

        statements = []
        for value_id, value in enumerate(discrete_values):
            statements.append(f"// {value}")
            if value in leaf_ids_by_value:
                leaf_groups = combine_leaf_groups(leaf_ids_by_value[value])
                statements.append(f"logic [0:{len(leaf_groups)-1}] g{value_id};")
                statements.append(f"reg [0:{len(leaf_groups)-1}] g{value_id}_reg;")
                for group_id, group in enumerate(leaf_groups):
                    statements.append(f"assign g{value_id}[{group_id}] = {group};")

                statements.append(f"""
    always_ff @(posedge clk) begin
        g{value_id}_reg <= g{value_id};
    end
    """)

                sum_groups = [f"g{value_id}_reg[{i}]" for i in range(len(leaf_groups))]
                statements.extend(generate_leaf_prefix_summer(value_id, sum_groups))
            else:
                statements.append(f"assign val[{value_id}] = 0;")
            statements.append(f"")

        leaf_count = leaf_id
        return f"""module leaf_counter_{classifier_id}(input logic clk, input logic [0:{leaf_count-1}] l, output logic [7:0] val [0:{len(discrete_values)-1}]);
    integer i;
\t{"\n\t".join(statements)}
endmodule"""

    return "\n\n\n".join([get_classifier_module(classifier_id, classifier_trees) for classifier_id, classifier_trees in classifiers.items()])


def generate_classifier_module(classifiers):
    return f"""
module mnist_classifier(input logic clk, input logic [0:783] image, output logic [3:0] digit);
    logic [7:0] score [0:9];
    integer i;
    
{"\n\n\n".join([
    f'''    // Digit {i}
    wire [0:{sum([len(tree) for tree in trees])-1}] leaf_{i};
    wire [7:0] val_count_{i} [0:12];
    wire [7:0] score_{i};
    (* preserve, noprune *) reg [0:783] image_{i}_reg;
    reg [0:{sum([len(tree) for tree in trees])-1}] leaf_{i}_reg;
    reg [7:0] val_count_{i}_reg [0:12];
    decision_tree_leaves_{i} dtl_{i} (.f(image_{i}_reg), .leaf(leaf_{i}));
    leaf_counter_{i} lc_{i} (.clk(clk), .l(leaf_{i}_reg), .val(val_count_{i}));
    counter_adder ca_{i} (.clk(clk), .val(val_count_{i}_reg), .score(score_{i}));
    
    always_ff @(posedge clk) begin
        image_{i}_reg <= image;
        leaf_{i}_reg <= leaf_{i};
        for (i = 0; i < 13; i = i + 1)
            val_count_{i}_reg[i] <= val_count_{i}[i];
        score[{i}] <= score_{i};
    end
    '''
    for i, trees in classifiers.items()
])}

    // Get maximum score
    max_value_index mvi(.clk(clk), .score(score), .digit(digit));
endmodule"""


def write_source_file(path, content):
    module_header = "// AUTOGENERATED DO NOT EDIT\n\n`timescale 1ns / 1ps\n\n"
    with open(f"./fpga/hdl/{path}", "w") as f:
        f.write(module_header + content)


if __name__ == "__main__":
    file_path = "model.json"
    data = json.load(open(file_path, 'r'))

    trees = [extract_tree(tree) for tree in data]
    classifiers = group_trees_by_classifier(trees)

    decision_tree_module = generate_decision_tree_module(classifiers)
    counter_module = generate_leaf_counter_module(classifiers)
    classifier_module = generate_classifier_module(classifiers)

    write_source_file("decision_trees.sv", decision_tree_module)
    write_source_file("leaf_counters.sv", counter_module)
    write_source_file("mnist_classifier.sv", classifier_module)
