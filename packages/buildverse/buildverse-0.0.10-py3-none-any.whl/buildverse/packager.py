if True:
    pass


class Packager:
    def __init__(self, subdir: str):
        raise Exception(subdir)

    def build(self):
        pass

    @staticmethod
    def create_arg_parser(parser):
        parser.add_argument("subdir", type=str, default=None, help="")
        # parser.add_argument("--subdir", type=str, default=None, help="")
        # parser.add_argument("--output", type=str, default=None, help="")
        # parser.add_argument("--embedexe", type=str, default=None, help="")
        return parser

    @staticmethod
    def arg_handler(args):
        raise Exception(args)
        Packager(args.subdir).build()
