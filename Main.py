from splitter import Splitter
parser = argparse.ArgumentParser()
parser.add_argument("video_path", help="")
parser.add_argument("path_where_to_save", help="")
args = parser.parse_args()
splitter = Splitter(args.video_path)
splitter.get_points()
splitter.make_videos(args.path_where_to_save)
