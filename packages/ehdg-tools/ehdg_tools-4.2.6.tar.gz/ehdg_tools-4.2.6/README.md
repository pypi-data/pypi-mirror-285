# EYE HEALTH DIAGNOSTIC GROUP's TOOLS (ehdg_tools)
Python library for eye health diagnostic group of Auckland Bioengineering Institude.

## List of Tools
1.  TinyFillBuffer  

### TinyFillBuffer
#### Buffer Length
It is the buffer to fill the gap between the data.  
The size of the gap that can be filled depands on the size of the buffer.  

##### For example:  
To fill the 10 data length gap, the buffer length must be atleast 12 because it needs 1 valid data at the front and at the back to be referenced.  
Default size of the buffer is 7.  
The minimum size of the buffer is 3.    

#### Fill Method
As we are dealing with pupil data, most of our data are float.  
Any nan data, zero data or string data between float data will be assumed as the gap.  
##### For example: 
In the x_value column in csv,  
340.33  
350.33  
NaN  
NaN  
380.33  

It will note that there is 2 data length gap and will be filled as follow:  
340.33  
350.33  
360.33  
370.33  
380.33  
In this case, the buffer length must be atleast 4.  

The other data column apart from float column such as string or image will be keep as it is because there is no valid data to be referenced.  
#### Class Attribute
##### self.buffer  
The main buffer which is handling the filling function.
##### self.buffer_max_length  
The length of buffer which can be initiated.
##### self.previous_data  
The data recently released from the buffer.  
##### self.data_attribute_array  
The attribute array of the data such as x_value, y_value.  
It starts as empty array and when the first data come in, it records the data attribute.  

#### Installation
```
pip install ehdg_tools
```

#### To upgrade the python library
```
pip install ehdg_tools -U
```

#### Usage in Python
```
from ehdg_tools.ehdg_buffers import TinyFillBuffer
import numpy as np

fill_buffer = TinyFillBuffer(7)

example_valid_data = {"x_value": 7, "y_value": 10}
example_gap_data = {"x_value": "Nan", "y_value": np.nan}
count = 0

while True:
    if count % 2 == 0:
        return_data = fill_buffer.add(example_valid_data)
    else:
        return_data = fill_buffer.add(example_gap_data)
    print(return_data)
    count += 1
```
In this code, the while loop is adding the example_valid_data when the count is even and adding the example_gap_data when the count is odd.  
But the return_data will be all valid data.
