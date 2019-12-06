# UR_Playground
 
Simple software that takes svg files with colored paths and converts them to Robot commands.
Meant to be used as an instructional tool for workshops with universal robots. Students can start to experiment directly without learning new software.
SVG files created in illustrator or inkscape are used to control the robot. By specifying an origin coordinate these 2D files can be positioned in space.

Acknowledgements:
python-urx
robot-simulator

___

### to do:
- [ ] parse
    - [x] plunge depth
    - [x] rotation values conversion
    - [ ] ~~reverse plunge / move direction~~


- [ ] visualise
    - [x] add origin point in visualisation
    - [X] change robot model
    - [x] make robot model responsive
    - [ ] calibrate starting angles
    - [ ] inverse kinematics
    - [ ] load environment

- [ ] simulate
    - [ ] everything

- [ ] send
    - [x] change tcp orientation
    - [x] connect button
    - [x] change units
    - [ ] add robot status
    - [ ] connect to robot button
    - [x] test unit change
    - [ ] thread / parallelise sending process to avoid freezing the program

- [ ] other
    - [ ] logging
    - [ ] connect logging to UI
    - [ ] documentation
    - [ ] test rotation

- [ ] save

- [ ] Package
    - [ ] create packages
      - [ ] Windows
      - [ ] Mac
      - [ ] (Linux)

- [x] TEST
- [ ] TEST
- [ ] Test !!!!
