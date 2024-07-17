# import necessary libraries
# import os
# os.environ['SAPHIRA_URL'] = 'http://localhost:8081'
import saphira 

class Radar:
    def get_radar_reading():
        raise Exception()

# define function to test radar state machine 
test_radar_state_machine = compile(saphira.get_param('2771eea4-8deb-4e43-9462-bcbedf40a8b1.json', 'Braking'), '<string>', "exec")
        
# try to get the radar reading from Radar class 
try:
    radar_reading = Radar.get_radar_reading()
# if there is an error, update test status to False 
except Exception as e:
    saphira.update_test_status('2771eea4-8deb-4e43-9462-bcbedf40a8b1.json', 'Braking', exception=e)
# if successful, update test status to True 
else:
    saphira.update_test_status('2771eea4-8deb-4e43-9462-bcbedf40a8b1.json', 'Braking', True)