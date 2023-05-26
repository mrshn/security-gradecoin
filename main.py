from satoshi_nakamoto import SatoshiNakamoto

import argparse
if __name__ == "__main__":
        parser = argparse.ArgumentParser()
        parser.add_argument("--host", default="localhost", help="Host address to bind to")
        parser.add_argument("--port", type=int, default=1423, help="Port number to bind to")
        args = parser.parse_args()

        owner_of_the_house = SatoshiNakamoto()
        owner_of_the_house.start()