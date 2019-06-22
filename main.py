import click
import requests
import yaml

base_url = "{}.com/api/v4/projects/{}/repository/tags"


def data_yamls(path):
    with open(path, "r") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as exc:
            print(exc)
            return 2


def update_yaml(path, dictionary):
    with open(path, "w") as f:
        yaml.dump(dictionary, f)


@click.command()
@click.option("--file", "yaml_file", prompt=True, help="Path to your yaml file")
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode")
@click.option("-u", "--update", is_flag=True, help="Update the yamls to latest tags")
def tags(update, verbose, yaml_file):
    data = data_yamls(yaml_file)
    for i, entry in enumerate(data):
        link = entry["src"]
        git_tag = entry["version"]

        base, project = link.split(".com/")
        project = project.replace(".git", "").replace("/", "%2F")
        repo_tags = requests.get(base_url.format(base, project), verify=False).json()

        # check the first tag as they are sorted in descending order
        latest_tag = repo_tags[0]["name"]
        if verbose and latest_tag == git_tag:
            print("[INFO] OK for {}".format(link))
        else:
            print(
                "[ERROR] latest tag for {} is {} but you have {}".format(
                    link, latest_tag, git_tag
                )
            )

            if update:
                # need to convert the tag to str to not write it as !!python/unicode
                data[i]["version"] = str(latest_tag)
                update_yaml(yaml_file, data)


if __name__ == "__main__":
    tags()