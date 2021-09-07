#from hwpc import model
from config import gch

if __name__ == '__main__':
    # m = model.Model()
    # m.run()

    test = gch.download_file('hwpcarbon-data','hpwc-user-inputs/user_request_20210907_123956/harvest_data_type')
    test.read()
    test.close()
    print('done')
