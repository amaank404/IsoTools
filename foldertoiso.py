import pyiso
from gooey import Gooey, GooeyParser
import os


def extract_paths(path: str):
    path_part = path.split("/")
    possible_paths = []
    for x in range(1, len(path_part)):
        possible_paths.append("/".join(path_part[0:x]))
    return possible_paths


def convert_folder_to_iso(folder: str, file: str, pass_on_args: dict, args, bootable: bool):
    if os.path.isfile(file):
        try:
            os.remove(file)
        except PermissionError:
            pass

    dirs = []
    files = []
    actual_files = []

    print("progress: 0/0")

    for r, d, f in os.walk(folder):
        dirs.extend(["/" + (r + "/" + x)[len(folder):] for x in d])
        files.extend(["/" + (r + "/" + x)[len(folder):] for x in f])
        actual_files.extend([os.path.join(r, x) for x in f])

    for x in range(len(dirs)):
        item = dirs[x]
        item = item.replace("\\", "/")
        item = item.replace("//", "/")
        dirs[x] = item

    for x in range(len(files)):
        item = files[x]
        item = item.replace("\\", "/")
        item = item.replace("//", "/")
        files[x] = item

    dirs2 = set(dirs)

    for x in dirs:
        dirs2.update(extract_paths(x))

    dirs = list(dirs2)

    if "" in dirs:
        dirs.remove("")

    dirs.sort()

    print(repr(dirs) + "\n")
    print(repr(files) + "\n")

    total = len(dirs) + len(files) + 1 + 1 if bootable else 0
    done = 0

    print(f"progress: {done}/{total}")

    iso = pyiso.IsoFile(file, **pass_on_args)

    for x in dirs:
        print(f"Dir: {x}")
        iso.new_dir(x)
        done += 1
        print(f"progress: {done}/{total}")

    for x, n in zip(actual_files, files):
        print(f"File: {x}, Iso_name: {n}")
        fp = open(x, "rb")
        iso.write(n, fp)
        done += 1
        print(f"progress: {done}/{total}")

    if bootable:
        done += 1
        print("Making Bootable")
        iso.make_bootable("/BOOT", open(args.bootfile, 'rb'), args.bootable == "isohybrid")
        print(f"progress: {done}/{total}")

    print("Saving Iso")
    done += 1

    iso.close()

    print(f"progress: {done}/{total}")


@Gooey(progress_regex=r"progress: (?P<p>[0-9]+)/(?P<o>[0-9]+)", progress_expr="p / o * 100")
def main():
    parser = GooeyParser(prog="Folder To Iso Converter", description="Convert folders to ISO files")
    parser.add_argument("folder_name", metavar="Folder Name", help="Folder to convert to iso", widget="DirChooser")
    parser.add_argument("output_file", metavar="Output File Name", help="Output Iso File Name", widget="FileSaver")
    parser.add_argument("-f", "--format", help="Format for the file",
                        choices=["udf 2.60", "joliet 1", "joliet 2", "joliet 3", "iso9660"], default="udf 2.60",
                        widget="Dropdown")
    parser.add_argument("-r", "--rock-ridge", help="rock ridge extension (Not Recommended)",
                        choices=["1.09", "1.10", "1.12", "none"], default="none", widget="Dropdown")
    parser.add_argument("-b", "--bootable", help="make iso bootable",
                        choices=["isohybrid", "eltorito", "none"], default="none", widget="Dropdown")
    parser.add_argument("-bf", "--bootfile", help="Provide only if you select to make iso bootable",
                        widget="FileChooser")
    args = parser.parse_args()
    kwargs = {}
    if args.format == "udf 2.60":
        kwargs["udf"] = "2.60"
        kwargs["rock_ridge"] = None
        kwargs["joliet"] = None
        kwargs["iso9660"] = False
    elif args.format == "joliet 1":
        kwargs["udf"] = False
        kwargs["rock_ridge"] = None
        kwargs["joliet"] = 1
        kwargs["iso9660"] = False
    elif args.format == "joliet 2":
        kwargs["udf"] = False
        kwargs["rock_ridge"] = None
        kwargs["joliet"] = 2
        kwargs["iso9660"] = False
    elif args.format == "joliet 3":
        kwargs["udf"] = False
        kwargs["rock_ridge"] = None
        kwargs["joliet"] = 3
        kwargs["iso9660"] = False
    elif args.format == "iso9660":
        kwargs["udf"] = False
        kwargs["rock_ridge"] = None
        kwargs["joliet"] = None
        kwargs["iso9660"] = True
    if args.rock_ridge != 'none':
        kwargs["rock_ridge"] = "1.09"
    convert_folder_to_iso(args.folder_name, args.output_file, pass_on_args=kwargs, args=args,
                          bootable=args.bootable != 'none')


if __name__ == '__main__':
    main()
