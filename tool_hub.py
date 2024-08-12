import argparse
def main():
    parser = argparse.ArgumentParser(description="CLI interface for uploading and downloading from Tool Hub.")
    parser.add_argument('action', type=str, choices=['u','d'],help='Upload or download a file.')
    parser.add_argument('fptn',type=str,help='For uploading this specifies the file path to the tools folder. For downloading this specifies the tool name.')
    args=parser.parse_args()
    action=args.action
    if action=='u':
        #read in file from file path
        pass
    else:
        #download tool from tool hub
        pass

if __name__=="__main__":
    main()