from srai_core.tools_docker import list_ecr_images


def main():
    dict_list_images = list_ecr_images()
    for repo_name, list_images in dict_list_images.items():
        print(f"Images in repository: {repo_name}")
        for image_tag in list_images:
            print(f"{repo_name}:{image_tag}")


if __name__ == "__main__":
    main()
