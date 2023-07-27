def remove_last_three_chars(string):
    new_string = string[:-3]
    return new_string

'''
import googlemaps

def calculate_distance(origin, destination, api_key):
    gmaps = googlemaps.Client(key=api_key)
    directions = gmaps.directions(origin, destination, mode="driving")
    
    if directions:
        distance_total = directions[0]['legs'][0]['distance']['text']
        duration_total = directions[0]['legs'][0]['duration']['text']
        steps = directions[0]['legs'][0]['steps']
        
        distance_highway = 0
        distance_not_highway = 0
        
        for step in steps:
            distance = step['distance']['text']
            instructions = step['html_instructions']
            print(instructions)

            if 'highway' in instructions.lower() or 'parkway' in instructions.lower() or 'hwy' in instructions.lower() or 'pkwy' in instructions.lower() or 'expy' in instructions.lower() or 'i-' in instructions.lower():
                print('grah' + instructions)

                distance_highway += step['distance']['value']
            else:
                distance_not_highway += step['distance']['value']
            
        distance_highway = round(distance_highway / 1609.34, 2)  # Convert meters to miles
        distance_not_highway = round(distance_not_highway / 1609.34, 2)  # Convert meters to miles
        
        print(f"Total Distance: {distance_total}")
        print(f"Total Duration: {duration_total}")
        print(f"Distance on Highway: {distance_highway} miles")
        print(f"Distance not on Highway: {distance_not_highway} miles")
    else:
        print("No directions found.")

# Replace 'YOUR_API_KEY' with your actual API key
api_key = 'AIzaSyA3J6HpIlBJPImcDVE384ZoDW-_znRH4Cw'
origin = '12 Poplar Lane, Commack, New York'
destination = '41-25 Kissena Blvd, Flushing, New York'

calculate_distance(origin, destination, api_key)
'''

# this is the code without separating highway and local 
import googlemaps

def calculate_distance(origin, destination, mpg, costOfGas, api_key):
    gmaps = googlemaps.Client(key=api_key)
    directions = gmaps.directions(origin, destination, mode="driving")
    
    if directions:
        distance = directions[0]['legs'][0]['distance']['text']
        duration = directions[0]['legs'][0]['duration']['text']
        steps = directions[0]['legs'][0]['steps']
        distance = float(remove_last_three_chars(distance))
        print(f"Distance: {distance}")
        print("Cost: " + str(round(float(distance) * (1 / mpg) * costOfGas, 2)))
        '''print(f"Duration: {duration}")
        print("Steps:")
        for step in steps:
            print(step['html_instructions'])
            print("-----")'''  
    else:
        print("No directions found.")

# Replace 'YOUR_API_KEY' with your actual API key
api_key = 'AIzaSyA3J6HpIlBJPImcDVE384ZoDW-_znRH4Cw'
#origin = input("Origin address: ")
origin = '12 Poplar Lane, Commack, New York'
#destination = input("Destination address: ")
#origin = '2020 Jericho Tpke, Commack, New York'
destination = '155 Harned Road, Commack, New York'
mpg = 25
costOfGas = 3.50

calculate_distance(origin, destination, mpg, costOfGas, api_key)

