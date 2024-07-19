# ProtoTwin Connect Client

This package provides a simple client that can be used to interface with ProtoTwin Connect.

## Basic Example

```
# STEP 1: Import the ProtoTwin client
import prototwin
import asyncio
import math

# STEP 2: Define your signal addresses (obtain these from your ProtoTwin model)
simulation_time_address = 0
motor_target_velocity_address = 3

async def main():
    # STEP 3: Start ProtoTwin Connect
    client = await prototwin.start()

    # STEP 4: Create the simulation loop
    while True:
        t = client.get(simulation_time_address) # Read signal values
        client.set(motor_target_velocity_address, math.sin(t)) # Write signal values
        await client.step() # Step the simulation forward in time

asyncio.run(main()) # Run the simulation loop
```