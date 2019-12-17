from splitter import Splitter, get_diff
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("video_path", help="")
parser.add_argument("mode", help="Save video parts? [y]/[n]")
parser.add_argument("path_where_to_save", help="")
args = parser.parse_args()

splitter = Splitter(args.video_path)
splitter.find_points()
if args.mode == 'y':
  splitter.make_videos(args.path_where_to_save)
  print('Videos are saved')
else:
  print(splitter.get_points())

