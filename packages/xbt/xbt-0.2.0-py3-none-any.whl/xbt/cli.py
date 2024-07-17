import os
import click
import yaml
from jinja2 import Environment, FileSystemLoader
import networkx as nx
from .models import load_all_models, load_all_scripts
from .macros import load_macros, load_macros_from_dir, load_macros_from_config
from .connections import build_connection
from dotenv import load_dotenv

env = Environment(loader=FileSystemLoader(["flow"]))


@click.group(chain=True, invoke_without_command=True)
@click.pass_context
def main(ctx):
    load_dotenv(".env")
    if ctx.invoked_subcommand is None:
        ctx.invoke(build)
        ctx.invoke(run)


@main.command("build")
def build():
    with open("build.yml") as fd:
        build_info = yaml.safe_load(fd)

    dag = nx.DiGraph()

    macros = load_macros(env, dag, build_info)
    env.globals.update(macros)
    macros = load_macros_from_dir(env)
    env.globals.update(macros)
    macros = load_macros_from_config(build_info)
    env.globals.update(macros)

    os.makedirs("build", exist_ok=True)

    models = {}
    models.update(load_all_models(env, dag, build_info))
    models.update(load_all_scripts(env, dag, build_info))

    for name, model in sorted(models.items()):
        template = env.get_template(model["template"])
        ty = model["type"]
        output = model["output"]
        fn = f"build/{output}"
        print(f"render {ty} {fn}")
        env.globals.update(current_node=name)
        rendered = template.render(model["data"])
        with open(fn, "w") as fd:
            fd.write(rendered)

    with open("build/graph.yml", "w") as fd:
        yaml.safe_dump(
            {
                "edges": list(dag.edges()),
                "nodes": {n: dag.nodes[n]["conn"] for n in dag.nodes()},
                "connections": build_info["connections"],
            },
            default_flow_style=False,
            stream=fd,
        )


@main.command("run")
@click.option(
    "-s",
    "--select",
    multiple=True,
    default=(),
)
@click.option(
    "-v",
    "--var",
    multiple=True,
)
@click.option("--dry-run/--no-dry-run", "-d/-D", default=False)
def run(select, dry_run, var):

    with open("build/graph.yml") as fd:
        graph = yaml.safe_load(fd)

    connections = {}
    for name, info in graph["connections"].items():
        connections[name] = build_connection(info)

    dag = nx.DiGraph()
    for node, conn in graph["nodes"].items():
        dag.add_node(node, conn=conn)
    for a, b in graph["edges"]:
        dag.add_edge(a, b)

    selected = set(graph["nodes"].keys())
    if select:
        selected = set()
        and_descendants = False
        and_ancestors = False
        for s in select:
            if s.endswith("+"):
                s = s[:-1]
                and_descendants = True
            if s.startswith("+"):
                s = s[1:]
                and_ancestors = True

            selected.add(s)
            if and_descendants:
                selected |= set(nx.descendants(dag, s))
            if and_ancestors:
                selected |= set(nx.ancestors(dag, s))

    for node in nx.topological_sort(dag):
        conn_name = dag.nodes[node]["conn"]
        if node not in selected:
            print(f"Skip {node} (not selected)")
            continue
        conn = connections[conn_name]
        print(f"Execute {node} using connection {conn_name}")
        with open(f"build/{node}.sql") as fd:
            query = fd.read()
            if not dry_run:
                conn.execute(query)


if __name__ == "__main__":
    main()
