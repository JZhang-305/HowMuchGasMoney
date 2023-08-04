import googlemaps
import streamlit as st
import pandas as pd

# Replace 'YOUR_API_KEY' with your actual API key
api_key = st.secrets['api_key']




def get_geocode(address, gmaps):
    geocode_result = gmaps.geocode(address)
    if geocode_result:
        return geocode_result[0]['geometry']['location']
    else:
        return None

def remove_last_three_chars(string):
    new_string = string[:-3]
    return new_string

def remove_commas(input_string):
    return input_string.replace(",", "")

def calculate_cost(distance, mpg, costOfGas):
    return round(float(distance) * (1 / mpg) * costOfGas, 2)

# Refactor the main functionality
def calculate_distance(api_key, origin, destination, mpg, costOfGas, roundtrip=False, pickup=[]):
    # list of addresses for map
    list_of_addresses = {'origin': origin, 'destination': destination}
    list_of_addresses['pickup'] = pickup

    total_extra_distance = 0
    total_extra_duration = 0
    total_extra_cost = 0

    gmaps = googlemaps.Client(key=api_key)

    solo_directions = gmaps.directions(origin, destination, mode="driving", units='imperial')
    

    
    
    if len(pickup) == 0:
        # just generate origin to destination
        directions = solo_directions

    #elif len(pickup) == 1:
        #directions = gmaps.directions(origin, destination, waypoints=pickup, mode="driving", optimize_waypoints=True, units='imperial')
    
    else:
        directions = gmaps.directions(origin, destination, waypoints=pickup, mode="driving", optimize_waypoints=True, units='imperial')
    


    if directions and solo_directions:
        # calculate cost, distance, and duration if you were to drive just yourself
        solo_distance = float(solo_directions[0]['legs'][0]['distance']['text'].split()[0])
        solo_duration = solo_directions[0]['legs'][0]['duration']['text']
        solo_cost = calculate_cost(solo_distance, mpg, costOfGas)
        # print("distance if i went solo: " + str(solo_distance))
        # print("duration if i went solo: " + str(solo_duration))
        # print("cost if i went solo: " + str(solo_cost))

        # calculate with picking people up
        distance = 0
        duration = []
        
        for leg in directions[0]['legs']:
            
            distance += float(leg['distance']['text'].split()[0])
            duration.append(leg['duration']['text']) 
            # duration += float(leg['duration']['text'].split()[0])

            # prints the start and end for each leg of the trip
            #print("Start: " + leg['start_address'])
            #print("End: " + leg['end_address'])
        
        cost = calculate_cost(distance, mpg, costOfGas)

        
        # # old code for formatting
        # try:
        #     distance = float(remove_last_three_chars(distance))
        # except ValueError:
        #     distance = float(remove_last_three_chars(distance).replace(",", ""))
        
        
        distance = round(distance, 2)
        # print(f"Distance: {distance}")
        # print("Cost: " + str(cost))
        # print(f"Duration: {duration}")

        
        # # code to generate the steps of the trip
        # for leg in directions[0]['legs']:
        #     steps = leg['steps']
        #     print("Steps:")
        #     for step in steps:
        #         print(step['html_instructions'])
        #         print("-----")
        

        if len(pickup) != 0:
            # figuring out the extras
            extra_distance = round(distance - solo_distance, 2)
            extra_cost = round(cost - solo_cost, 2)
            total_extra_distance += extra_distance
            total_extra_cost += extra_cost
            #print("extra distance: " + str(extra_distance) + " mi")
            #print("extra cost: $" + str(extra_cost))
        else:
            #print(f"Distance: {distance}")
            #print("Cost: " + str(cost))
            #print(f"Duration: {duration}")
            pass

    else:
        print("No directions found.")
        return False



    if roundtrip:
        # flip flopping the order
        #print('\nCost for driving everyone home')

        # info if you just drove yourself home, commented out because of api pricing
        #solo_directions = gmaps.directions(destination, origin, mode="driving", units='imperial')

        solo_distance = float(solo_directions[0]['legs'][0]['distance']['text'].split()[0])
        solo_duration = solo_directions[0]['legs'][0]['duration']['text']
        solo_cost = calculate_cost(solo_distance, mpg, costOfGas)
        # print("distance if i went solo: " + str(solo_distance))
        # print("duration if i went solo: " + str(solo_duration))
        # print("cost if i went solo: " + str(solo_cost))

        # info if you drive everyone home too
        distance = 0
        duration = []
        # commented out bc of api pricing
        #directions = gmaps.directions(destination, origin, waypoints=pickup, mode="driving", optimize_waypoints=True, units='imperial')
        if directions:
            for leg in directions[0]['legs']:
                
                distance += float(leg['distance']['text'].split()[0])
                duration.append(leg['duration']['text']) 
                #duration += float(leg['duration']['text'].split()[0])

                # prints the start and end for each leg of the trip
                #print("Start: " + leg['start_address'])
                #print("End: " + leg['end_address'])

            distance = round(distance, 2)

            cost = calculate_cost(distance, mpg, costOfGas)

            # print(f"Distance: {distance}")
            # print("Cost: " + str(cost))
            # print(f"Duration: {duration}")

            if len(pickup) != 0:
                extra_distance = round(distance - solo_distance, 2)
                extra_cost = round(cost - solo_cost, 2)
                total_extra_distance += extra_distance
                total_extra_cost += extra_cost
                #print("extra distance: " + str(extra_distance) + " mi")
                #print("extra cost: $" + str(extra_cost))
                #print()
                total_extra_distance = round(total_extra_distance, 2)
                total_extra_cost = round(total_extra_cost, 2)
                #print('total extra distance: ' + str(total_extra_distance) + " mi")
                #print('total extra cost: $' + str(total_extra_cost))
                #print('each person owes: $' + str(round(total_extra_cost/len(pickup), 2)))
            else:
                pass
                #print(f"Distance: {distance}")
                #print("Cost: " + str(cost))
                #print(f"Duration: {duration}")

        else:
            print("No directions found.")
            return False

    # Instead of printing to the console, return the results as a dict
    return {
        'solo_distance': solo_distance,
        'solo_cost': solo_cost,
        'distance': distance,
        'cost': cost,
        'duration': duration,
        'total_extra_distance': total_extra_distance,
        'total_extra_cost': total_extra_cost,
        'list_of_addresses': list_of_addresses,
        'gmaps': gmaps,
    }


# Variables for user inputs
st.title("How Much For ⛽")
st.write("For when cheap friends ask to get picked up, just charge them! Or you can use this to calculate gas from A to B with no pickups but what's the fun in that!")
#origin = st.text_input("Origin Address 🚩", value = "12 Poplar Lane, Commack NY 11725", placeholder="where u start from")
origin = st.text_input("Origin Address 🚩", placeholder="where u start from")
#destination = st.text_input("Destination Address 💹", value = "2020 Jericho Tpke, Commack NY 11725", placeholder = "where u going")
destination = st.text_input("Destination Address 💹", placeholder = "where u going")

#pickup_addresses = []
#address = st.text_input("Pickup Address 🐋", value="155 Harned Road, Commack NY 11725")
#if address:
    #pickup_addresses.append(address)

# A dynamic list of input fields for pickup addresses
pickup_addresses = []
#address = st.text_input("Pickup Address 🐋")

for i in range(3):
     #if i == 0:
        #address = st.text_input(f"Pickup Address {i + 1} 🐋")
     #else:
     address = st.text_input(f"Pickup Address {i + 1} 🐋", placeholder = 'optional')
     if address:
         pickup_addresses.append(address)

mpg = st.number_input("Enter the Miles Per Gallon (MPG) of your vehicle", min_value=0.0, value=25.0)
# "Averages: Coupe - xxx, Crossover - xxx, Sedan - xxx, Hatchback - xxx, SUV - xxx, Minivan - xxx, Truck - xxx"
cost_of_gas = st.number_input("Enter the cost of gas per gallon", min_value=0.0, value=3.50)

if len(pickup_addresses) != 0:
    roundtrip = st.checkbox(label = "Are you driving them home too?")
else:
    roundtrip = False
st.write("**P.S.** The average mpg is 25.0 and gas is like 3.50 right now")
# When the calculate button is pressed
if st.button('Calculate ⛽'):
    results = calculate_distance(api_key, origin, destination, mpg, cost_of_gas, roundtrip=roundtrip, pickup=pickup_addresses)
    if results:
        # if all directions were generated correctly

        # Display the results
        #st.write(f"Distance if I went solo: {results['solo_distance']}")
        #st.write(f"Duration if I went solo: {results['solo_duration']}")
        #for idx, duration in enumerate(results['duration']):
            #st.write(f"Duration of leg {idx}: {duration}")
        #st.write(f"Cost if I went solo: ${results['solo_cost']}")
        #st.write(f"Total Distance: {results['distance']} mi")

        df = pd.DataFrame(columns=['lat', 'lon', 'size', 'color'])

        for address in results['list_of_addresses']:
            if type(results['list_of_addresses'][address]) != list:
                geo = get_geocode(results['list_of_addresses'][address], results['gmaps']) # get geocode
                if geo:
                    #df = df.append({'lat': geo['lat'], 'lon': geo['lng']}, ignore_index=True) # add to dataframe
                    #df.loc[len(df.index)] = [geo['lat'], geo['lng']]
                    if address == 'origin':
                        color = (255, 0, 0)
                        size = 150
                    elif address == 'destination':
                        color = (0, 255, 0)
                        size = 150
                    elif address == 'pickup':
                        color = (0, 0, 255)
                        size = 50
                    df.loc[len(df.index)] = [geo['lat'], geo['lng'], size, color]
            else:

                for pickup in results['list_of_addresses'][address]:
                    
                    geo = get_geocode(pickup, results['gmaps']) # get geocode
                    if geo:
                        #df = df.append({'lat': geo['lat'], 'lon': geo['lng']}, ignore_index=True) # add to dataframe
                        #df.loc[len(df.index)] = [geo['lat'], geo['lng']]
                        if address == 'origin':
                            color = (255, 0, 0)
                        elif address == 'destination':
                            color = (0, 255, 0)
                        elif address == 'pickup':
                            color = (0, 0, 255)
                        df.loc[len(df.index)] = [geo['lat'], geo['lng'], 100, color]
        # this is for adjusting the zoom

        # calculate bounding coordinates
        min_lat, max_lat = df['lat'].min() - 0.01, df['lat'].max() + 0.01
        min_lon, max_lon = df['lon'].min() - 0.01, df['lon'].max() + 0.01

        # add bounding coordinates to dataframe with small size
        df.loc[len(df.index)] = [min_lat, min_lon, 1, (255, 255, 255)]
        df.loc[len(df.index)] = [min_lat, max_lon, 1, (255, 255, 255)]
        df.loc[len(df.index)] = [max_lat, min_lon, 1, (255, 255, 255)]
        df.loc[len(df.index)] = [max_lat, max_lon, 1, (255, 255, 255)]

        st.map(df, size='size', color='color')
        st.write("**P.P.S.** By the way, red represents the starting location, green represents the destination, and blue represents any pickup locations")
        
        if len(results['list_of_addresses']['pickup']) == 0:
            st.write("The total distance is **" + str(results['solo_distance']) + " mi**")
            st.write("It's gonna cost **$" + str(results['solo_cost']) + "** in gas")
            st.write("It's gonna take **" + str(results['duration'][0]) + "**")

        elif results['total_extra_distance'] > 0:
            st.write("I have to drive **" + str(results['total_extra_distance']) + " mi** extra because of you 😠")
            st.write("It's gonna cost **$" + str(results['total_extra_cost']) + "** more in gas to pick you up 📉")
            st.write("Each of you owes **$" + str(round(results['total_extra_cost']/len(results['list_of_addresses']['pickup']), 2)) + "**")

        else:
            st.write("Driving you made us slower, but I actually drive **" + str(results['total_extra_distance'] * -1) + " mi** less because of you")
            st.write("I saved **$" + str(results['total_extra_cost'] * -1) + "** in gas money 💹")
        
        '''--------------------------------------------'''
        st.write("I'm a W UI designer - jz 7/28/2023")
        st.write("ibrahim owes me a lot of money")
        #st.write(results['list_of_addresses'])
    
    else:
        # if a route could not be determined
        st.write("your inputs are wack, no route could be found")
    
