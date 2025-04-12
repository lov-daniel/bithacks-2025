# Backend Server

## Protocol

Python REST api using flask; it returns results in json format.

### Data Points

Data points must be in json format and contain the following fields:
- timestamp: BSON compatible date time
- accel_x: floating point
- accel_y: floating point
- accel_z: floating_point


## Routes

### /

This route takes only GET requests, and returns an array of all the data points in the database.

### /insert-single/

This route takes GET and POST requests.

GET response is identical to that of `/`

POST response is identical to that of `/` after inserting the new data point. Each data point must have a `timestamp` field that includes a date-time.

POST body must match the following format:

```json
// data point
{
    "timestamp": // ISO date time
    "accel_x": // floating point
    "accel_y": // floating point
    "accel_z": // floating point
}
```

### /insert-batch/

This route takes GET and POST requests.

GET response is identical to that of `/`

POST response is identical to that of `/` after inserting the new data points. Each data point must have a `timestamp` field that includes a date-time.

POST body must match the following format:

```json
{
    data: [
        {
            // data point (same format as single insert)
        }, 
        {
             // data point (same format as single insert)
        }
    ]
}
```