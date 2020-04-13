import argparse

parser = argparse.ArgumentParser(description='Reddit bot for adding coffin meme videos')

parser.add_argument('--queue', '-q', action='store_false', default=True, help='Run in database queueing mode')