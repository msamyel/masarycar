# masarycar
Detecting cars in bikelanes at Masarycka.

## How to use

First, install the prerequisites
```
pip install -r requirements.txt
```

Next run the script:
```
python main.py  -f "src/sample01.jpeg" \
                -c "193,440,529,954" \
                -m "src/mask.png" \
                -u 5 \
                -a 1 \
                -d "src/cars.xml"
```

## List of arguments
-  `-f` `--file` Specify path to the file you want to analyze.
-  `-c` `--croprect` Specify cropping rect for the picture in order: left, top, right, bottom. Separated by commas.
- `-m` `--mask` Specify path to the mask file
- `-u` `--scaleup` Set magnify rate to resize the original image by.
- `-a` `--apply-corrections` Set 1 to apply corrections suggested [here](https://github.com/saineshnakra/Vehicle-detection-image-and-video/blob/main/VehicleDetection.ipynb), otherwise set 0.
- `-d` `--detection` Specify car detection XML file path