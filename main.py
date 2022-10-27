import sys
import src.greeter as greeter
import boto3
from gpsdclient import GPSDClient
import time
locationClient = boto3.client('location', region_name=sys.argv[4])

# get your data as json strings:
#with GPSDClient(host="127.0.0.1") as client:
#    for result in client.json_stream():
#        print(result)

# or as python dicts (optionally convert time information to `datetime` objects)
def get_values(trackerName, units, interval):
    with GPSDClient() as client:
        resultsArray = {}
        n = 0 
        for result in client.dict_stream(convert_datetime=True, filter=["TPV"]):
                n += 1
                lat = result.get("lat", "n/a")
                lon = result.get("lon", "n/a")
                speedms = result.get("speed", "n/a")
                elevationm = result.get("alt", "n/a")
                accuracy = result.get("ecefpAcc", "n/a")
                sampletime = result.get("time", "n/a")
                if units == "metric":
                    speed = speedms
                    elevation = elevationm
                elif units == "imperial":
                    speed = (speedms*2.2369362920544)
                    elevation = (elevationm * 3.280839895)
                if (n%int(interval)==0):
                    response = locationClient.batch_update_device_position(
                        TrackerName = trackerName,
                        Updates = [
                            {
                                'Accuracy': {
                                    'Horizontal': accuracy
                                },
                                'DeviceId': "Greengrass",
                                'Position': [
                                    lon,
                                    lat
                                ],
                                'PositionProperties': {
                                    'speed': str(speed),
                                    'elevation': str(elevation)
                                },
                                'SampleTime': sampletime
                            }
                        ]
                    )
                    print("Position Updated")
                else:
                    print("Position Not Updated")
                resultsArray.update({"lat": lat, "lon": lon, "speed": speed, "elevation": elevation, "accuracy": accuracy, "time": sampletime, "count": n, "trackerName": trackerName})
                
                print(resultsArray)
def main():
    TrackerName = sys.argv[1]
    Units = sys.argv[2]
    interval = sys.argv[3]
    get_values(TrackerName, Units, interval)

if __name__ == "__main__":
    main()
