import googlemaps
import streamlit as st
import pandas as pd

# Fetch API key from Streamlit secrets
api_key = st.secrets['api_key']

# Set up page configuration
st.set_page_config(page_title="How Much For Gas")

# Function to retrieve geocode (latitude and longitude) from a given address
def get_geocode(address, gmaps):
    geocode_result = gmaps.geocode(address)
    if geocode_result:
        return geocode_result[0]['geometry']['location']
    else:
        return None

# Utility functions
def remove_last_three_chars(string):
    return string[:-3]

def remove_commas(input_string):
    return input_string.replace(",", "")

# Function to calculate the total gas cost based on distance, MPG, and gas price
def calculate_cost(distance, mpg, costOfGas):
    return round(float(distance) * (1 / mpg) * costOfGas, 2)

# Main function to calculate driving distances, duration, and gas costs
def calculate_distance(api_key, origin, destination, mpg, costOfGas, roundtrip=False, pickup=[]):
    list_of_addresses = {'origin': origin, 'destination': destination, 'pickup': pickup}
    total_extra_distance = 0
    total_extra_cost = 0

    # Initialize Google Maps API client
    gmaps = googlemaps.Client(key=api_key)

    # Get driving directions from origin to destination
    solo_directions = gmaps.directions(origin, destination, mode="driving", units='imperial')
    
    if len(pickup) == 0:
        # Only origin to destination without pickups
        directions = solo_directions
    else:
        # Include waypoints for pickup locations
        directions = gmaps.directions(origin, destination, waypoints=pickup, mode="driving", optimize_waypoints=True, units='imperial')

    if directions and solo_directions:
        # Calculate solo trip distance, duration, and cost
        solo_distance = float(solo_directions[0]['legs'][0]['distance']['text'].split()[0])
        solo_duration = solo_directions[0]['legs'][0]['duration']['text']
        solo_cost = calculate_cost(solo_distance, mpg, costOfGas)

        # Calculate total distance and cost with pickups (if any)
        distance = sum(float(leg['distance']['text'].split()[0]) for leg in directions[0]['legs'])
        duration = [leg['duration']['text'] for leg in directions[0]['legs']]
        cost = calculate_cost(distance, mpg, costOfGas)

        if len(pickup) != 0:
            extra_distance = round(distance - solo_distance, 2)
            extra_cost = round(cost - solo_cost, 2)
            total_extra_distance += extra_distance
            total_extra_cost += extra_cost

    else:
        st.write("No directions found.")
        return False

    # Handle roundtrip calculations
    if roundtrip:
        # Optional handling for driving back to origin
        pass  # Implement if needed

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

# UI elements for user input
st.title("How Much For ⛽")
st.header("HowMuchForGas.com")
st.write("Calculate gas costs for trips with optional pickups.")

origin = st.text_input("Origin Address 🚩", placeholder="Enter your starting point")
destination = st.text_input("Destination Address 💹", placeholder="Enter your destination")

pickup_addresses = []
for i in range(3):
    address = st.text_input(f"Pickup Address {i + 1} 🐋", placeholder='Optional')
    if address:
        pickup_addresses.append(address)

mpg = st.number_input("Enter your vehicle's MPG", min_value=0.0, value=25.0)
cost_of_gas = st.number_input("Enter the cost of gas per gallon", min_value=0.0, value=3.50)

if len(pickup_addresses) != 0:
    roundtrip = st.checkbox("Are you driving them home too?")
else:
    roundtrip = False

st.write("Average MPG is 25.0 and gas is around $3.50 per gallon.")

# Calculate button action
if len(origin) != 0 and len(destination) != 0 and st.button('Calculate ⛽'):
    results = calculate_distance(api_key, origin, destination, mpg, cost_of_gas, roundtrip=roundtrip, pickup=pickup_addresses)
    if results:
        df = pd.DataFrame(columns=['lat', 'lon', 'size', 'color'])
        for address in results['list_of_addresses']:
            if isinstance(results['list_of_addresses'][address], list):
                for pickup in results['list_of_addresses'][address]:
                    geo = get_geocode(pickup, results['gmaps'])
                    if geo:
                        color, size = (0, 0, 255), 100
                        df.loc[len(df.index)] = [geo['lat'], geo['lng'], size, color]
            else:
                geo = get_geocode(results['list_of_addresses'][address], results['gmaps'])
                if geo:
                    if address == 'origin':
                        color, size = (255, 0, 0), 150
                    elif address == 'destination':
                        color, size = (0, 255, 0), 150
                    df.loc[len(df.index)] = [geo['lat'], geo['lng'], size, color]

        st.map(df, size='size', color='color')
        st.write("**Legend:** Red = Start, Green = Destination, Blue = Pickup")

        # Display calculated results
        st.write(f"The total distance is **{results['solo_distance']} mi**")
        st.write(f"It's gonna cost **${results['solo_cost']}** in gas")
    else:
        st.write("Invalid inputs, no route found.")

